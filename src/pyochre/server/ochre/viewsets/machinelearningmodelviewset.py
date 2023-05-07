import logging
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import MachineLearningModelSerializer, MachineLearningModelTopicModelSerializer, MachineLearningModelHuggingfaceSerializer, MachineLearningModelStarcoderSerializer
from pyochre.server.ochre.models import MachineLearningModel
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
from pyochre.server.ochre.autoschemas import OchreAutoSchema
import requests


logger = logging.getLogger(__name__)


class MachineLearningModelViewSet(OchreViewSet):
    model = MachineLearningModel
    queryset = MachineLearningModel.objects.all()
    schema = OchreAutoSchema(
        tags=["machinelearningmodel"],
        component_name="machinelearningmodel",
        operation_id_base="machinelearningmodel",
        response_serializer=MachineLearningModelSerializer
    )

    def get_serializer_class(self):
        if self.action == "train_topic_model":
            return MachineLearningModelTopicModelSerializer
        elif self.action == "import_huggingface_model":
            return MachineLearningModelHuggingfaceSerializer
        elif self.action == "create_starcoder_model":
            return MachineLearningModelStarcoderSerializer
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
            #print(response)
            #print(response.reason)
            out = response.json()
            return Response(out)
        
        #print(out)
        #    return Response({"status" : "success"})

    @action(
        detail=False,
        methods=["post", "options"],
        url_path="create/topic_model"
    )
        
    def create_model(self, request, pk=None):
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
    
    @action(detail=False, methods=["POST"], url_path="create/topicmodel")
    def train_topic_model(self, request, pk=None):
        """
        Create a topic model
        """
        return self.create_model(request, pk=None)
        
    @action(detail=False, methods=["POST"], url_path="create/huggingface")
    def import_huggingface_model(self, request, pk=None):
        """
        Import a HuggingFace model
        """
        return self.create_model(request, pk=None)

    @action(detail=False, methods=["POST"], url_path="create/starcoder")
    def create_starcoder_model(self, request, pk=None):
        """
        Create a StarCoder model
        """
        return self.create_model(request, pk=None)
    
