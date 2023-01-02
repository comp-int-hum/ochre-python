import json
import logging
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import PrimarySourceSerializer
from pyochre.server.ochre.models import PrimarySource
from pyochre.server.ochre.renderers import OchreRenderer
from pyochre.server.ochre.parsers import OchreParser


logger = logging.getLogger(__name__)


class PrimarySourceViewSet(OchreViewSet):
    serializer_class = PrimarySourceSerializer
    model = PrimarySource
    schema = AutoSchema(
        tags=["primarysource"],
        component_name="primarysource",
        operation_id_base="primarysource"
    )

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

    @action(detail=True, methods=["get"], renderer_classes=[OchreRenderer])
    def sparqlquery(self, request, pk=None):
        obj = PrimarySource.objects.get(id=pk)
        resp = obj.query(request.query_params)
        
        retval = HttpResponse(
            json.dumps(resp.json),
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
