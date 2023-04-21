import logging
from rest_framework.schemas.openapi import AutoSchema
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import SlideSerializer
from pyochre.server.ochre.models import Slide


logger = logging.getLogger(__name__)


class SlideViewSet(OchreViewSet):
    serializer_class = SlideSerializer
    model = Slide
    schema = AutoSchema(
        tags=["slide"],
        component_name="slide",
        operation_id_base="slide",
    )
