import logging
from rest_framework.schemas.openapi import AutoSchema
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import AnnotationSerializer
from pyochre.server.ochre.models import Annotation


logger = logging.getLogger(__name__)


class AnnotationViewSet(OchreViewSet):
    serializer_class = AnnotationSerializer
    model = Annotation
    schema = AutoSchema(
        tags=["annotation"],
        component_name="annotation",
        operation_id_base="annotation",
    )
