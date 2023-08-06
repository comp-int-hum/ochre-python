import logging
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import SlideSerializer, SlideInteractiveSerializer, SlideUploadSerializer, PermissionsSerializer
from pyochre.server.ochre.models import Slide
from pyochre.server.ochre.autoschemas import OchreAutoSchema
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer


logger = logging.getLogger(__name__)


class SlideViewSet(OchreViewSet):
    list_template_name = "ochre/template_pack/slideshow.html"
    model = Slide
    #queryset = Slide.objects.all()
    schema = OchreAutoSchema(
        tags=["slide"],
        component_name="slide",
        operation_id_base="slide",
    )
    create_template_name = "ochre/template_pack/slide_create.html"
    
    def get_serializer_class(self):
        if self.action == "create_from_uploads":
            return SlideUploadSerializer
        elif isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer):
            return SlideInteractiveSerializer
        else:
            return SlideSerializer

    @action(
        detail=False,
        methods=["POST", "GET"],
        url_path="create/from_uploads",
        url_name="create_from_uploads"
    )    
    def create_from_uploads(self, request, pk=None):
        if request.method == "GET":
            ser = self.get_serializer_class()()
            return Response(ser.data)
        elif request.method == "POST":
            ser = self.get_serializer_class()(
                data=request.data,
                context={"request" : request}
            )
            if ser.is_valid():
                obj = Slide.objects.create(
                    name=ser.validated_data["name"],
                    created_by=ser.validated_data["created_by"],
                    article=ser.validated_data["article_file"].read() if "article_file" in ser.validated_data else None,
                    image=ser.validated_data["image_file"],
                    active=ser.validated_data.get("active", False),
                    ordering=ser.validated_data.get("ordering", 0)
                )
                obj.save()
                return Response({"status" : "success"})
            else:
                return Response(
                    ser.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
    
    def list(self, request, pk=None):
        return self._list(request)

    def retrieve(self, request, pk=None):
        """
        """
        return self._retrieve(request, pk=pk)

    def destroy(self, request, pk=None):
        return self._destroy(request, pk)

    def create(self, request, pk=None):
        return self._create(request)
    
    @action(
        detail=True,
        methods=["GET", "PATCH"],
        serializer_class=PermissionsSerializer
    )
    def permissions(self, request, pk=None):
        return self._permissions(request, pk)
