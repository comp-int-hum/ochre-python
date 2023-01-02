import logging
from django.urls import path
from django.views.generic import TemplateView
from pyochre.server.ochre.models import PrimarySource, Query, Annotation


logger = logging.getLogger(__name__)


app_name = "primary_sources"
urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="ochre/template_pack/accordion.html",
            extra_context={
                "items" : [
                    PrimarySource,
                    Query,
                    Annotation
                ]
            }
        ),
        name="index"
    )
]
