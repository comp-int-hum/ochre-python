import logging
from rest_framework.schemas.openapi import AutoSchema
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import AnnotationSerializer, AnnotationInteractiveSerializer, ComputationalAnnotationSerializer, HumanAnnotationSerializer
from pyochre.server.ochre.models import Annotation
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
from rest_framework.decorators import action
from pyochre.server.ochre.autoschemas import OchreAutoSchema


logger = logging.getLogger(__name__)


class AnnotationViewSet(OchreViewSet):
    model = Annotation
    queryset = Annotation.objects.all()
    schema = OchreAutoSchema(
        tags=["annotation"],
        component_name="annotation",
        operation_id_base="annotation",
        response_serializer=AnnotationSerializer        
    )

    def get_serializer_class(self):
        if isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer):
            return AnnotationInteractiveSerializer
        elif self.action == "create_human_annotation":
            return HumanAnnotationSerializer
        elif self.action == "create_computational_annotation":
            return ComputationalAnnotationSerializer        
        else:
            return AnnotationSerializer

    @action(detail=True, methods=["get"])
    def interaction(self, request, pk=None):        
        pass

    @action(
        detail=False,
        methods=["post"],
        serializer_class=ComputationalAnnotationSerializer
    )
    def create_computational_annotation(self, request, pk=None):
        pass

    @action(
        detail=False,
        methods=["post"],
        serializer_class=HumanAnnotationSerializer
    )
    def create_human_annotation(self, request, pk=None):
        pass
