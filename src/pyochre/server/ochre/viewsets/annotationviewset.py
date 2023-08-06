import logging
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import AnnotationSerializer, AnnotationComputationalSerializer, AnnotationHumanSerializer, AnnotationInteractiveSerializer, PermissionsSerializer
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

    def get_template_names(self):
        if isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer) and self.action == "retrieve":
            return ["ochre/template_pack/tabs.html"]
        return super(AnnotationViewSet, self).get_template_names()
    
    def get_serializer_class(self):
        if self.action == "create_human_annotation":
            return AnnotationHumanSerializer
        elif self.action == "create_computational_annotation":
            return AnnotationComputationalSerializer
        elif isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer):
            return AnnotationInteractiveSerializer
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
        methods=["GET", "POST"],
        url_path="create/computational_annotation",
        url_name="create_computational_annotation"
    )
    def create_computational_annotation(self, request, pk=None):
        if request.method == "GET":
            ser = self.get_serializer_class()()
            return Response(ser.data)
        else:
            return self.create_annotation(request, pk)

    @action(
        detail=False,
        methods=["GET", "POST"],
        url_path="create/human_annotation",
        url_name="create_human_annotation"
    )
    def create_human_annotation(self, request, pk=None):
        if request.method == "GET":
            ser = self.get_serializer_class()()
            return Response(ser.data)
        else:
            return self.create_annotation(request, pk)        

    def list(self, request, pk=None):
        """
        List annotations.
        """
        return self._list(request)

    def retrieve(self, request, pk=None):
        """
        Get information about a particular annotation.
        """
        return self._retrieve(request, pk=pk)

    def destroy(self, request, pk=None):
        """
        Destroy (delete) an annotation.
        """
        return self._destroy(request, pk)
        
    @action(
        detail=True,
        methods=["GET", "PATCH"],
        serializer_class=PermissionsSerializer
    )
    def permissions(self, request, pk=None):
        return self._permissions(request, pk)
