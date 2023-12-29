import logging
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import FileSerializer, PermissionsSerializer
from pyochre.server.ochre.models import File
from pyochre.server.ochre.autoschemas import OchreAutoSchema
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
import magic


logger = logging.getLogger(__name__)


class FileViewSet(OchreViewSet):
    model = File
    schema = OchreAutoSchema(
        tags=["file"],
        component_name="file",
        operation_id_base="file",
    )
    list_template_name = "ochre/template_pack/file_list.html"
    listentry_view_template_name = "ochre/template_pack/file_listentry_view.html"
    listentry_create_template_name = "ochre/template_pack/file_listentry_create.html"
    
    def get_serializer_class(self):
        return FileSerializer
    
    def list(self, request, pk=None):
        return self._list(request)

    def retrieve(self, request, pk=None):
        return self._retrieve(request, pk=pk)

    def destroy(self, request, pk=None):
        return self._destroy(request, pk)

    def create(self, request, pk=None):
        retval = self._create(request)
        f = File.objects.get(id=retval.data["id"])
        with f.item.open(mode="rb") as ifd:
            tp = magic.from_buffer(ifd.read(2048), mime=True)
        if tp.startswith("image"):
            f.is_image = True
            f.save()
        return retval

    def partial_update(self, request, pk=None):
        return self._partial_update(request, pk)
    
    @action(
        detail=True,
        methods=["GET", "PATCH"],
        serializer_class=PermissionsSerializer
    )
    def permissions(self, request, pk=None):
        return self._permissions(request, pk)
