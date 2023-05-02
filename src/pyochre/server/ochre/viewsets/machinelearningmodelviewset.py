import logging
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import MachineLearningModelSerializer, MachineLearningModelInteractiveSerializer, TopicModelSerializer
from pyochre.server.ochre.models import MachineLearningModel
from pyochre.server.ochre.tasks import apply_machinelearningmodel, train_topic_model
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
        if self.action == "create_topic_model":
            return TopicModelSerializer
        if isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer):
            return MachineLearningModelInteractiveSerializer
        else:
            return MachineLearningModelSerializer


    #def create_topic_model(self, request, pk=None):
    #    return Response()
        
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
    def create_topic_model(self, request, pk=None):
        """
        Create a topic model
        """
        ser = TopicModelSerializer(data=request.data, context={"request" : request})
        if ser.is_valid():
            
            
            train_topic_model.delay(
                primarysource_id=ser.validated_data["primarysource"].id,
                query_id=ser.validated_data["query"].id if ser.validated_data.get("query") else None,
                user_id=ser.validated_data["created_by"].id,
                **{k : v for k, v in ser.validated_data.items() if k not in ["primarysource", "created_by", "query"]}
            )
            return Response({"status" : "success"})
        else:
            return Response(ser.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods=["POST"], url_path="create/starcoder_model")
    # def create_starcoder_model(self, request, pk=None):
    #     """
    #     Create a StarCoder model
    #     """
    #     pass
