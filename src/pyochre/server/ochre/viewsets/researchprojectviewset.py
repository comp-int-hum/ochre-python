import logging
from rest_framework.decorators import action
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import ResearchProjectSerializer, PermissionsSerializer
from pyochre.server.ochre.models import ResearchProject
from pyochre.server.ochre.autoschemas import OchreAutoSchema


logger = logging.getLogger(__name__)


class ResearchProjectViewSet(OchreViewSet):

    model = ResearchProject
    schema = OchreAutoSchema(
       tags=["researchproject"],
       component_name="researchproject",
       operation_id_base="researchproject",
    )
    listentry_view_template_name = "ochre/template_pack/researchproject_listentry_view.html"
    
    def get_serializer_class(self):
        return ResearchProjectSerializer

    def list(self, request, pk=None):
        return self._list(request)

    def retrieve(self, request, pk=None):
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
    
