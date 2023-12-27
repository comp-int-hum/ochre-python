import logging
from rest_framework.decorators import action
from pyochre.server.ochre.serializers import UserSerializer, PermissionsSerializer
from pyochre.server.ochre.models import User
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.autoschemas import OchreAutoSchema


logger = logging.getLogger(__name__)


class UserViewSet(OchreViewSet):
    model = User
    schema = OchreAutoSchema(
        tags=["user"],
        component_name="user",
        operation_id_base="user"
    )
    listentry_view_template_name = "ochre/template_pack/user_listentry_view.html"    

    def get_queryset(self):
        return super(UserViewSet, self).get_queryset().exclude(username="AnonymousUser")
    
    def get_serializer_class(self):
        return UserSerializer

    def list(self, request, pk=None):
        return self._list(request)

    def retrieve(self, request, pk=None):
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
