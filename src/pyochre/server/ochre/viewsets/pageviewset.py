import logging
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import PageSerializer, PermissionsSerializer
from pyochre.server.ochre.models import Page
from pyochre.server.ochre.autoschemas import OchreAutoSchema
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer


logger = logging.getLogger(__name__)


class PageViewSet(OchreViewSet):
    model = Page
    schema = OchreAutoSchema(
        tags=["page"],
        component_name="page",
        operation_id_base="page",
    )
    detail_view_template_name = "ochre/template_pack/page_detail_view.html"
    
    def get_serializer_class(self):
        return PageSerializer

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
