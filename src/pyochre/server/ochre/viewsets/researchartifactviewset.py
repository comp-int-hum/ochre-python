import logging
from rest_framework.schemas.openapi import AutoSchema
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import ResearchArtifactSerializer
from pyochre.server.ochre.models import ResearchArtifact


logger = logging.getLogger(__name__)


class ResearchArtifactViewSet(OchreViewSet):
    serializer_class = ResearchArtifactSerializer
    model = ResearchArtifact
    schema = AutoSchema(
        tags=["researchartifact"],
        component_name="researchartifact",
        operation_id_base="researchartifact",
    )
