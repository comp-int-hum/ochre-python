import logging
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.viewsets import ViewSet
from pyochre.server.ochre.serializers import UserSerializer
from pyochre.server.ochre.models import User
from pyochre.server.ochre.viewsets import OchreViewSet


logger = logging.getLogger(__name__)


class UserViewSet(OchreViewSet):
    serializer_class = UserSerializer
    model = User
    schema = AutoSchema(
        tags=["user"],
        component_name="user",
        operation_id_base="user"
    )
