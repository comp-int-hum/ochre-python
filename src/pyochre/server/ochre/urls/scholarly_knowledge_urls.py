import logging
from django.urls import path
from django.views.generic import TemplateView
from pyochre.server.ochre.models import Annotation
from pyochre.server.ochre.serializers import AnnotationHumanSerializer, AnnotationComputationalSerializer


logger = logging.getLogger(__name__)


urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="ochre/template_pack/ochre.html",
            extra_context={
                "items" : [
                    {
                        "title" : "Annotations",
                        "view_name" : "api:annotation-list",
                        "model" : Annotation,
                        "create" : {
                            "Human" : "api:annotation-create_human_annotation",
                            "Machine learning" : "api:annotation-create_computational_annotation",
                        }
                    }
                ],
                "uid" : "scholarly_knowledge"
            }
        ),
        name="index"
    )
]
