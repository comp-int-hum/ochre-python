import json
import logging
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import PrimarySourceSerializer, PrimarySourceHathiTrustSerializer, PrimarySourceXslTransformationSerializer, PrimarySourceMaterialsSerializer, MaterialSerializer, PrimarySourceFinalizeMaterialsSerializer, PrimarySourceInteractiveSerializer, PermissionsSerializer
from pyochre.server.ochre.models import PrimarySource
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
from pyochre.server.ochre.autoschemas import OchreAutoSchema


logger = logging.getLogger(__name__)


class PrimarySourceViewSet(OchreViewSet):
    model = PrimarySource
    queryset = PrimarySource.objects.all()
    schema = OchreAutoSchema(
        tags=["primarysource"],
        component_name="primarysource",
        operation_id_base="primarysource",
        response_serializer=PrimarySourceSerializer
    )
    detail_template_name = "ochre/template_pack/tabs.html"
    # def get_template_names(self):
    #     if isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer) and self.action == "retrieve" and self.request.headers["Mode"] == "view":
    #         return ["ochre/template_pack/tabs.html"]
    #     return super(PrimarySourceViewSet, self).get_template_names()
    
    def get_serializer_class(self):
        if self.action == "create_from_hathi_trust":
            return PrimarySourceHathiTrustSerializer
        elif self.action == "create_from_xsl_transformation":
            return PrimarySourceXslTransformationSerializer
        elif self.action == "finalize_materials":
            return PrimarySourceFinalizeMaterialsSerializer        
        elif self.action in ["missing_materials", "add_missing_materials"]:
            return PrimarySourceMaterialsSerializer        
        elif isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer) and self.action == "list":
            return PrimarySourceSerializer
        elif isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer) and self.request.headers.get("Mode") == "view":
            return PrimarySourceInteractiveSerializer        
        else:
            return PrimarySourceSerializer

    @action(
        detail=True,
        methods=["GET"],
    )
    def domain(self, request, pk=None):
        ps = PrimarySource.objects.get(id=pk)
        return Response(json.loads(ps.domain.serialize(format="json-ld")))
    
    @action(
        detail=True,
        methods=["GET"],
    )
    def data(self, request, pk=None):
        ps = PrimarySource.objects.get(id=pk)
        return Response(json.loads(ps.data.serialize(format="json-ld")))
            
    @action(
        detail=False,
        methods=["POST", "GET"],
        url_path="create/from_hathi_trust",
        url_name="create_from_hathitrust_collection"
    )
    def create_from_hathi_trust(self, request, pk=None):
        """
        Create a primary source from a HathiTrust collection file.
        """
        if request.method == "GET":
            ser = self.get_serializer_class()()
            return Response(ser.data)
        else:
            ser = self.get_serializer_class()(
                data=request.data,
                context={"request" : request}
            )
            if ser.is_valid():
                logger.info("Creating new primarysource")
                obj = ser.create(ser.validated_data)
                resp_ser = PrimarySourceSerializer(obj, context={"request" : request})
                return Response(resp_ser.data)
            else:
                return Response(
                    ser.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=False,
        methods=["POST", "GET"],
        url_path="create/from_xsl_transformation",
        url_name="create_from_xsl_transformation"
    )
    def create_from_xsl_transformation(self, request, pk=None):
        """
        Create a primary source from data and a custom XSL transformation.
        """
        if request.method == "GET":
            ser = self.get_serializer_class()()
            return Response(ser.data)
        else:
            ser = self.get_serializer_class()(
                data=request.data,
                context={"request" : request}
            )
            if ser.is_valid():
                logger.info("Creating new primarysource")
                obj = ser.create(ser.validated_data)
                resp_ser = PrimarySourceSerializer(obj, context={"request" : request})
                return Response(resp_ser.data)
            else:
                return Response(
                    ser.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=True,
        methods=["GET"],
        url_path="missing_materials"
    )
    def missing_materials(self, request, pk=None):
        """
        List missing material files for the primary source.
        """
        ps = PrimarySource.objects.get(id=pk)
        missing = {
            str(b["fobj"]) : b["fname"].value for b in ps.query(
                """
                SELECT ?fobj ?fname WHERE {
                  ?x ochre:hasFile ?fobj .
                  ?fobj ochre:hasLabel ?fname .
                }
                """
            )
        }
        return Response({"missing_file_names" : missing})

    @action(
        detail=True,
        methods=["PUT"],
        url_path="add_missing_materials"
    )
    def add_missing_materials(self, request, pk=None):
        """
        Add missing materials files for the primary source.
        """
        # ps = PrimarySource.objects.get(id=pk)
        # missing = {
        #     b["fname"].value : b["type"] for b in ps.query(
        #         """
        #         SELECT ?fname ?type WHERE {
        #           ?x ochre:hasFile ?f .
        #           ?f ochre:hasLabel ?fname .
        #           ?f ochre:instanceOf ?type .
        #         }
        #         """
        #     )
        # }

        ser = self.get_serializer_class()(
            data=request.data,
            context={"request" : request}
        )
        if ser.is_valid():
            name = ser.validated_data["name"]
            logger.info("Adding missing material file")
            ms = MaterialSerializer()
            content = ser.validated_data["file"].read()
            ret = ms.create({"content" : content})
            mid = ret["material_id"]
            # resp = ps.update(
            #     """
            #     DELETE {
            #       ?f ochre:hasLabel '%s'
            #     }
            #     INSERT {
            #       ?f ochre:hasMaterialId '%s'
            #     }
            #     WHERE {
            #       ?x ochre:hasFile ?f .
            #       ?f ochre:hasLabel '%s' .
            #       ?f ochre:instanceOf ?type .
            #     }
            #     """ % (name, mid, name)
            # )
            return Response({"status" : "success", "material_id" : mid})
        else:
            return Response(
                ser.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(
        detail=True,
        methods=["POST"],
        url_path="finalize_materials"
    )
    def finalize_materials(self, request, pk=None):
        """
        Remove references to any material files that have not been satisfied.
        """
        ps = PrimarySource.objects.get(id=pk)
        values = """
        VALUES (?from ?to)
        {
          %s
        }
        """ % ("\n".join(["(\"{}\" \"{}\")".format(k, v) for k, v in request.data.items()]))
        resp = ps.update(
            """
            INSERT {
              ?fobj ochre:hasMaterialId ?to .
            }
            WHERE {
              %s
              ?x ochre:hasFile ?fobj .
              ?fobj ochre:hasLabel ?from .              
            }
            """ % (values)
        )
        if not resp.ok:
            return Response({"status" : resp.status_code, "reason" : resp.reason})
        resp = ps.update(
            """
            DELETE {
              ?fobj ochre:hasLabel ?fname .
            }
            WHERE {
              ?x ochre:hasFile ?fobj .
              ?fobj ochre:hasLabel ?fname .              
            }
            """
        )
        ps.infer_domain()
        return Response({"status" : resp.status_code, "reason" : resp.reason})
        
    def list(self, request, pk=None):
        """
        List primary sources.
        """
        return self._list(request)

    def retrieve(self, request, pk=None):
        """
        Get information about a particular primary source.
        """
        return self._retrieve(request, pk=pk)

    def destroy(self, request, pk=None):
        """
        Destroy (delete) a primary source.
        """
        return self._destroy(request, pk)

    @action(
        detail=True,
        methods=["GET", "PATCH"],
        serializer_class=PermissionsSerializer
    )
    def permissions(self, request, pk=None):
        """
        Get or modify permissions information about a primary source.
        """
        return self._permissions(request, pk)
