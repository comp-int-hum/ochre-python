import logging
from rest_framework.decorators import action
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import QuerySerializer, QueryInteractiveSerializer, QueryFromFileSerializer, QueryFromTextSerializer, PermissionsSerializer
from pyochre.server.ochre.models import Query, PrimarySource
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
from pyochre.server.ochre.autoschemas import OchreAutoSchema


logger = logging.getLogger(__name__)


class QueryViewSet(OchreViewSet):
    model = Query
    queryset = Query.objects.all()
    schema = OchreAutoSchema(
        tags=["query"],
        component_name="query",
        operation_id_base="query",
    )
    permission_classes = []
    #detail_template_name = "ochre/template_pack/tabs.html"
    
    def get_serializer_class(self):
        if self.action == "create_from_file":
            return QueryFromFileSerializer
        elif self.action == "create_from_text":
            return QueryFromTextSerializer        
        elif isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer):
            return QueryInteractiveSerializer
        else:
            return QuerySerializer
    
    # @action(detail=True, methods=["POST"], name="Apply the query")
    # def perform(self, request, pk=None):
    #     q = Query.objects.get(id=request.data.get("query"))
    #     p = PrimarySource.objects.get(id=request.data.get("primarysource"))
    #     res = p.query(q.sparql)
    #     return Response(res) #.serialize(format="json"))

    def list(self, request, pk=None):
        """
        List queries.
        """
        return self._list(request)

    def retrieve(self, request, pk=None):
        """
        Get information about a particular query.
        """
        return self._retrieve(request, pk=pk)

    def destroy(self, request, pk=None):
        """
        Destroy (delete) a query.
        """
        return self._destroy(request, pk)

    @action(
        detail=True,
        methods=["GET", "PATCH"],
        serializer_class=PermissionsSerializer
    )
    def permissions(self, request, pk=None):
        """
        Get or modify permissions information about a query.
        """
        return self._permissions(request, pk=pk)
    
    @action(
        detail=False,
        methods=["POST", "GET"],
        url_path="create/from_text",
        url_name="create_from_text"
    )
    def create_from_text(self, request, pk=None):
        """
        Create a new query from SPARQL text.
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
                logger.info("Creating new query")
                obj = ser.create(ser.validated_data)
                resp_ser = QuerySerializer(obj, context={"request" : request})
                return Response(resp_ser.data)
            else:
                return Response(
                    ser.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=False,
        methods=["POST", "GET"],
        url_path="create/from_file",
        url_name="create_from_file"
    )
    def create_from_file(self, request, pk=None):
        """
        Create a new query from a SPARQL file.
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
                logger.info("Creating new query")
                obj = ser.create(ser.validated_data)
                resp_ser = QuerySerializer(obj, context={"request" : request})
                return Response(resp_ser.data)
            else:
                return Response(
                    ser.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
