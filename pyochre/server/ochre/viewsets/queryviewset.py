import logging
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import QuerySerializer
from pyochre.server.ochre.models import Query


logger = logging.getLogger(__name__)


class QueryViewSet(OchreViewSet):
    serializer_class = QuerySerializer
    model = Query
    schema = AutoSchema(
        tags=["query"],
        component_name="query",
        operation_id_base="query",
    )
