import logging
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.decorators import action
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import MachineLearningModelSerializer, MachineLearningModelInteractiveSerializer
from pyochre.server.ochre.models import MachineLearningModel
from pyochre.server.ochre.tasks import apply_machinelearningmodel
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
import requests

logger = logging.getLogger(__name__)


class MachineLearningModelViewSet(OchreViewSet):
    model = MachineLearningModel
    schema = AutoSchema(
        tags=["machinelearningmodel"],
        component_name="machinelearningmodel",
        operation_id_base="machinelearningmodel"
    )

    def get_serializer_class(self):
        if isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer):
            return MachineLearningModelInteractiveSerializer
        else:
            return MachineLearningModelSerializer
    
    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        if "primarysource_id" in request.data:
            apply_machinelearningmodel.delay(
                pk,
                request.data.get("name"),
                request.user.id,            
                request.data["primarysource_id"],
                request.data.get("query_id", None)
            )
            return Response({"status" : "success"})
        else:
            data = {k : v for k, v in request.data.items() if not isinstance(v, InMemoryUploadedFile)}
            files = {k : v for k, v in request.data.items() if isinstance(v, InMemoryUploadedFile)}
            response = requests.post(
                "{}/v2/models/{}/infer".format(
                    settings.TORCHSERVE_INFERENCE_ADDRESS,
                    pk
                    #model_id
                ),
                data=data,
                files=files
            )
            #print(request.data)
            print(response)
            #print(response.reason)
            out = response.json()
            return Response(out)
        
        #print(out)
        #    return Response({"status" : "success"})

    # @action(detail=False, methods=["POST"], url_path="create/topic_model")
    # def create_topic_model(self, request, pk=None):
    #     """
    #     Create a topic model
    #     """
    #     create_topic_model.delay(
    #         request.data.get("name"),
    #         request.user.id,            
    #         request.data.get("query"),
    #         request.data.get("primarysource"),
    #         lowercase=request.data.get("lowercase", True),
    #         topic_count=request.data.get("topic_count", 10)
    #     )
    #     return Response({"status" : "success"})

    # @action(detail=False, methods=["POST"], url_path="create/starcoder_model")
    # def create_starcoder_model(self, request, pk=None):
    #     """
    #     Create a StarCoder model
    #     """
    #     pass
