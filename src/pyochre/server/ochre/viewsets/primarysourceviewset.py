import json
import logging
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import PrimarySourceSerializer, PrimarySourceInteractiveSerializer
from pyochre.server.ochre.models import PrimarySource
from pyochre.server.ochre.renderers import OchreRenderer
from pyochre.server.ochre.parsers import OchreParser
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer


logger = logging.getLogger(__name__)


class PrimarySourceViewSet(OchreViewSet):
    model = PrimarySource
    schema = AutoSchema(
        tags=["primarysource"],
        component_name="primarysource",
        operation_id_base="primarysource"
    )
    
    def get_serializer_class(self):
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
