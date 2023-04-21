import logging
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.decorators import action
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import QuerySerializer, QueryInteractiveSerializer
from pyochre.server.ochre.models import Query, PrimarySource
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer


logger = logging.getLogger(__name__)


class QueryViewSet(OchreViewSet):
    model = Query
    schema = AutoSchema(
        tags=["query"],
        component_name="query",
        operation_id_base="query",
    )

    def get_serializer_class(self):
        if isinstance(
                self.request.accepted_renderer,
                OchreTemplateHTMLRenderer
        ):
            return QueryInteractiveSerializer
        else:
            return QuerySerializer
    
    @action(detail=True, methods=["post"], name="Apply the query")
    def perform(self, request, pk=None):
        q = Query.objects.get(id=request.data.get("query"))
        p = PrimarySource.objects.get(id=request.data.get("primarysource"))
        res = p.query(q.sparql)
        return Response(res) #.serialize(format="json"))
