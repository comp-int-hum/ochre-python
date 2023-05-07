import logging
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import AnnotationSerializer, AnnotationComputationalSerializer, AnnotationHumanSerializer
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
        if self.action == "create_human_annotation":
            return AnnotationHumanSerializer
        elif self.action == "create_computational_annotation":
            return AnnotationComputationalSerializer        
        else:
            return AnnotationSerializer

    def create_annotation(self, request, pk=None):
        ser = self.get_serializer_class()(
            data=request.data,
            context={"request" : request}
        )
        if ser.is_valid():
            ser.create(ser.validated_data)
            return Response({"status" : "success"})
        else:
            return Response(
                ser.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(
        detail=False,
        methods=["post"],
        url_path="create/computational_annotation"
    )
    def create_computational_annotation(self, request, pk=None):
        return self.create_annotation(request, pk)

    @action(
        detail=False,
        methods=["post"],
        url_path="create/human_annotation"
    )
    def create_human_annotation(self, request, pk=None):
        return self.create_annotation(request, pk)        
