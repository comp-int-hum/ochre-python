import logging
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import ArticleSerializer, PermissionsSerializer
from pyochre.server.ochre.models import Article
from pyochre.server.ochre.autoschemas import OchreAutoSchema
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer


logger = logging.getLogger(__name__)


class ArticleViewSet(OchreViewSet):
    list_template_name = "ochre/template_pack/article_list.html"
    detail_template_name = "ochre/template_pack/article_detail.html"
    model = Article
    #queryset = Slide.objects.all()
    schema = OchreAutoSchema(
        tags=["article"],
        component_name="article",
        operation_id_base="article",
    )
    #create_template_name = "ochre/template_pack/article_create.html"
    
    def get_serializer_class(self):
        return ArticleSerializer

    def get_template_names(self):
        if self.request.headers.get("mode") == "archive":
            if self.action == "list":
                return ["ochre/template_pack/archive_list.html"]
            elif self.action == "retrieve":
                return ["ochre/template_pack/archive_detail.html"]
        else:
            return super(ArticleViewSet, self).get_template_names()
    # @action(
    #     detail=False,
    #     methods=["POST", "GET"],
    #     url_path="create/from_uploads",
    #     url_name="create_from_uploads"
    # )    
    # def create_from_uploads(self, request, pk=None):
    #     if request.method == "GET":
    #         ser = self.get_serializer_class()()
    #         return Response(ser.data)
    #     elif request.method == "POST":
    #         ser = self.get_serializer_class()(
    #             data=request.data,
    #             context={"request" : request}
    #         )
    #         if ser.is_valid():
    #             obj = Article.objects.create(
    #                 name=ser.validated_data["name"],
    #                 created_by=ser.validated_data["created_by"],
    #                 content=ser.validated_data["article_file"].read() if "article_file" in ser.validated_data else None,
    #                 image=ser.validated_data["image_file"],
    #                 active=ser.validated_data.get("active", False),
    #                 ordering=ser.validated_data.get("ordering", 0)
    #             )
    #             obj.save()
    #             return Response({"status" : "success"})
    #         else:
    #             return Response(
    #                 ser.errors,
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    
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

    def partial_update(self, request, pk=None):
        return self._partial_update(request, pk)
    
    @action(
        detail=True,
        methods=["GET", "PATCH"],
        serializer_class=PermissionsSerializer
    )
    def permissions(self, request, pk=None):
        return self._permissions(request, pk)