import logging
from django.urls import path
from django.views.generic import TemplateView
from pyochre.server.ochre.models import MachineLearningModel
from pyochre.server.ochre.serializers import MachineLearningModelTopicModelSerializer, MachineLearningModelHuggingfaceSerializer, MachineLearningModelStarcoderSerializer

logger = logging.getLogger(__name__)


urlpatterns = [
    path(
        '',
        TemplateView.as_view(
            template_name="ochre/template_pack/ochre.html",
            extra_context={
                "items" : [
                    {
                        "title" : "Computational models",
                        "view_name" : "api:machinelearningmodel-list",
                        "model" : MachineLearningModel,
                        "creation_methods" : [
                            {
                                "title" : "Topic model",
                                "url" : "api:machinelearningmodel-create_topic_model",
                            },
                            {
                                "title" : "Huggingface",
                                "url" : "api:machinelearningmodel-create_huggingface_model"
                            },
                            {
                                "title" : "StarCoder",
                                "url" : "api:machinelearningmodel-create_starcoder_model"
                            }
                        ]
                    }
                ],
                "uid" : "machine_learning"
            }
        ),
        name="machine_learning"
    )
]
