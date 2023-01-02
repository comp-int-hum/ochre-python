import logging
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.viewsets import ViewSet
from pyochre.server.ochre.serializers import DocumentationSerializer
from pyochre.server.ochre.models import Documentation
from pyochre.server.ochre.viewsets import OchreViewSet


logger = logging.getLogger(__name__)


class DocumentationViewSet(OchreViewSet):
    serializer_class = DocumentationSerializer
    model = Documentation
    schema = AutoSchema(
        tags=["documentation"],
        component_name="documentation",
        operation_id_base="documentation"
    )
