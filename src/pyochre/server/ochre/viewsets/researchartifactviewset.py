import logging
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.decorators import action
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import ResearchArtifactSerializer, PermissionsSerializer
from pyochre.server.ochre.models import ResearchArtifact
from pyochre.server.ochre.autoschemas import OchreAutoSchema


logger = logging.getLogger(__name__)


class ResearchArtifactViewSet(OchreViewSet):

    model = ResearchArtifact
    schema = OchreAutoSchema(
       tags=["researchartifact"],
       component_name="researchartifact",
       operation_id_base="researchartifact",
    )
    detail_template_name = "ochre/template_pack/researchartifact_detail.html"
    #edit_template_name = "ochre/template_pack/researchartifact_edit.html"
    list_template_name = "ochre/template_pack/researchartifact_list.html"

    def get_serializer_class(self):
        return ResearchArtifactSerializer

    def list(self, request, pk=None):
        return self._list(request)

    def retrieve(self, request, pk=None):
        """
        """
        return self._retrieve(request, pk=pk)

    def destroy(self, request, pk=None):
        return self._destroy(request, pk)
    
    def create(self, request, pk=None):
        return self._create(request)

    def partial_update(self, request, pk=None):
        return self._partial_update(request, pk)

    @action(
        detail=True,
        methods=["GET", "PATCH"],
        serializer_class=PermissionsSerializer
    )
    def permissions(self, request, pk=None):
        return self._permissions(request, pk)
    
