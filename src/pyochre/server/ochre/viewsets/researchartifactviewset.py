import logging
from rest_framework.schemas.openapi import AutoSchema
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import ResearchArtifactSerializer
from pyochre.server.ochre.models import ResearchArtifact
from pyochre.server.ochre.autoschemas import OchreAutoSchema


logger = logging.getLogger(__name__)


class ResearchArtifactViewSet(OchreViewSet):
    serializer_class = ResearchArtifactSerializer
    model = ResearchArtifact
    queryset = ResearchArtifact.objects.all()
    schema = OchreAutoSchema(
       tags=["researchartifact"],
       component_name="researchartifact",
       operation_id_base="researchartifact",
    )
