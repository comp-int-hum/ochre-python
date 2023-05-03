import json
import logging
from django.http import HttpResponse
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import PrimarySourceSerializer, PrimarySourceInteractiveSerializer, HathiTrustSerializer
from pyochre.server.ochre.models import PrimarySource
from pyochre.server.ochre.renderers import OchreRenderer
from pyochre.server.ochre.parsers import OchreParser
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
from pyochre.server.ochre.autoschemas import OchreAutoSchema
from pyochre.server.ochre.tasks import primarysource_from_hathitrust_collection


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
    
    def get_serializer_class(self):
        if self.action == "create_hathi_trust":
            return HathiTrustSerializer
        if isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer):
            return PrimarySourceInteractiveSerializer
        else:
            return PrimarySourceSerializer

    @action(detail=True, methods=["get"], name="Retrieve the domain definition")
    def domain(self, request, pk=None):
        obj = PrimarySource.objects.get(id=pk)
        return obj.domain()

    @action(detail=True, methods=["get"], name="Retrieve the data")
    def data(self, request, pk=None):
        obj = PrimarySource.objects.get(id=pk)
        return obj.data(limit=100)

    @action(detail=True, methods=["post"])
    def clear(self, request, pk=None):
        obj = PrimarySource.objects.get(id=pk)
        obj.clear()
        return Response(200)

    @action(detail=True, methods=["post"], renderer_classes=[OchreRenderer])
    def query(self, request, pk=None):
        obj = PrimarySource.objects.get(id=pk)
        resp = obj.query(request.data["query"]).serialize(format="json")
        retval = HttpResponse(
            resp,
            status=200,
            content_type="application/sparql-results+json"
        )
        return retval

    @action(
        detail=True,
        methods=["post"],
        renderer_classes=[OchreRenderer],
        parser_classes=[OchreParser]
    )
    def sparqlupdate(self, request, pk=None):
        obj = PrimarySource.objects.get(id=pk)
        resp = obj.update(request.data)
        return Response(
            status=200,
        )

    def update(self, request, pk=None):
        self.clear(request, pk)
        return super(PrimarySourceViewSet, self).update(request, pk=pk)
        
    def partial_update(self, request, pk=None):
        return super(PrimarySourceViewSet, self).update(request, pk=pk)

    @action(
        detail=False,
        methods=["post"],
        url_path="create/hathi_trust"
    )
    def create_hathi_trust(self, request, pk=None):
        """
        Create a primary source from a HathiTrust collection file.
        """
        ser = HathiTrustSerializer(data=request.data, context={"request" : request})
        if ser.is_valid():
            logger.info("Creating new primarysource")
            primarysource_from_hathitrust_collection.delay(
                ser.validated_data["collection_file"].read().decode("utf-8"),
                ser.validated_data["name"],
                ser.validated_data["created_by"].id
            )
            return Response({"status" : "success"})
        else:
            return Response(
                ser.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
