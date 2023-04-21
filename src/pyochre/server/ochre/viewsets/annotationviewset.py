import logging
from rest_framework.schemas.openapi import AutoSchema
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import AnnotationSerializer, AnnotationInteractiveSerializer
from pyochre.server.ochre.models import Annotation
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
from rest_framework.decorators import action


logger = logging.getLogger(__name__)


class AnnotationViewSet(OchreViewSet):
    model = Annotation
    schema = AutoSchema(
        tags=["annotation"],
        component_name="annotation",
        operation_id_base="annotation",
    )

    def get_serializer_class(self):
        if isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer):
            return AnnotationInteractiveSerializer
        else:
            return AnnotationSerializer

    @action(detail=True, methods=["get"])
    def interaction(self, request, pk=None):        
        pass
