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
    model = Article
    schema = OchreAutoSchema(
        tags=["article"],
        component_name="article",
        operation_id_base="article",
    )
    listentry_view_template_name = "ochre/template_pack/article_listentry_view.html"
    
    def get_serializer_class(self):
        return ArticleSerializer

    # def get_template_names(self):
    #     if self.request.headers.get("mode") == "archive":
    #         if self.action == "list":
    #             return ["ochre/template_pack/archive_list.html"]
    #         elif self.action == "retrieve":
    #             return ["ochre/template_pack/archive_detail.html"]
    #     else:
    #         return super(ArticleViewSet, self).get_template_names()
    
    def list(self, request, pk=None):
        return self._list(request)

    def retrieve(self, request, pk=None):
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
