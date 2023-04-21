import logging
from django.urls import path
from django.views.generic import TemplateView
from pyochre.server.ochre.models import MachineLearningModel


logger = logging.getLogger(__name__)


urlpatterns = [
    path(
        '',
        TemplateView.as_view(
            template_name="ochre/template_pack/accordion.html",
            extra_context={"items" : [MachineLearningModel]}
        ),
        name="index"
    ),
]
