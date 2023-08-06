import logging
from rest_framework.decorators import action
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.viewsets import ViewSet
from pyochre.server.ochre.serializers import UserSerializer, UserInteractiveSerializer, PermissionsSerializer
from pyochre.server.ochre.models import User
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.autoschemas import OchreAutoSchema
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer


logger = logging.getLogger(__name__)


class UserViewSet(OchreViewSet):
    model = User
    schema = OchreAutoSchema(
        tags=["user"],
        component_name="user",
        operation_id_base="user"
    )
    detail_template_name = "ochre/template_pack/user_detail.html"
    #edit_template_name = "ochre/template_pack/user_edit.html"
    list_template_name = "ochre/template_pack/generic_list.html"
    #accordion_header_template_name = "ochre/template_pack/user_accordion_header.html"
    #accordion_content_template_name = "ochre/template_pack/user_accordion_content.html"

    def get_queryset(self):
        return super(UserViewSet, self).get_queryset().exclude(username="AnonymousUser")
    
    def get_serializer_class(self):
        #if isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer) and self.request.headers.get("Mode") == "view":
        #    return UserInteractiveSerializer
        #else:
        return UserSerializer

    def list(self, request, pk=None):
        return self._list(request)

    def retrieve(self, request, pk=None):
        """
        """
        return self._retrieve(request, pk=pk)

    def destroy(self, request, pk=None):
        return self._destroy(request, pk)

    def partial_update(self, request, pk=None):
        return self._partial_update(request, pk)

    def create(self, request, pk=None):
        return self._create(request)
    
    @action(
        detail=True,
        methods=["GET", "PATCH"],
        serializer_class=PermissionsSerializer
    )
    def permissions(self, request, pk=None):
        return self._permissions(request, pk)
