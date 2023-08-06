import logging
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import MachineLearningModelSerializer, MachineLearningModelTopicModelSerializer, MachineLearningModelHuggingfaceSerializer, MachineLearningModelStarcoderSerializer, MachineLearningModelInteractiveSerializer, PermissionsSerializer
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
    detail_template_name = "ochre/template_pack/tabs.html"
    
    def get_serializer_class(self):
        if self.action == "create_topic_model":
            return MachineLearningModelTopicModelSerializer
        elif self.action == "create_huggingface_model":
            return MachineLearningModelHuggingfaceSerializer
        elif self.action == "create_starcoder_model":
            return MachineLearningModelStarcoderSerializer
        elif isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer) and self.action == "list":
            return MachineLearningModelSerializer        
        elif isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer) and self.request.headers.get("Mode") == "view":
            return MachineLearningModelInteractiveSerializer        
        else:
            return MachineLearningModelSerializer

    @action(
        detail=True,
        methods=["get"],
    )
    def properties(self, request, pk=None):
        mlm = MachineLearningModel.objects.get(id=pk)
        return Response(json.loads(mlm.properties.serialize(format="json-ld")))

    @action(
        detail=True,
        methods=["get"],
    )
    def signature(self, request, pk=None):
        mlm = MachineLearningModel.objects.get(id=pk)
        return Response(json.loads(mlm.signature.serialize(format="json-ld")))
        
    @action(detail=True, methods=["POST"]) # add "GET" but without breaking cmdline!
    def apply(self, request, pk=None):
        """
        Directly apply a model to directly-specified data.
        """
        data = {k : v for k, v in request.data.items() if not isinstance(v, InMemoryUploadedFile)}
        files = {k : v for k, v in request.data.items() if isinstance(v, InMemoryUploadedFile)}
        response = requests.post(
            "{}/v2/models/{}/infer".format(
                settings.TORCHSERVE_INFERENCE_ADDRESS,
                pk
            ),
            data=data,
            files=files
        )
        out = response.json()
        return Response(out)
        
    def create_model(self, request, pk=None):
        ser = self.get_serializer_class()(
            data=request.data,
            context={"request" : request}
        )
        if ser.is_valid():
            obj = ser.create(ser.validated_data)
            resp_ser = MachineLearningModelSerializer(obj, context={"request" : request})
            return Response(resp_ser.data)            
        else:
            return Response(
                ser.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(
        detail=False,
        methods=["POST", "GET"],
        url_path="create/topicmodel",
        url_name="create_topic_model"
    )
    def create_topic_model(self, request, pk=None):
        """
        Train a topic model.
        """
        if request.method == "GET":
            ser = self.get_serializer_class()()
            return Response(ser.data)
        else:
            return self.create_model(request, pk=None)
        
    @action(
        detail=False,
        methods=["POST", "GET"],
        url_path="create/huggingface",
        url_name="create_huggingface_model"
    )
    def create_huggingface_model(self, request, pk=None):
        """
        Import a HuggingFace model.
        """
        if request.method == "GET":
            ser = self.get_serializer_class()()
            return Response(ser.data)
        else:
            return self.create_model(request, pk=None)

    @action(
        detail=False,
        methods=["POST", "GET"],
        url_path="create/starcoder",
        url_name="create_starcoder_model"
    )
    def create_starcoder_model(self, request, pk=None):
        """
        Create a StarCoder model.
        """
        if request.method == "GET":
            ser = self.get_serializer_class()()
            return Response(ser.data)
        else:
            return self.create_model(request, pk=None)
    
    def list(self, request, pk=None):
        """
        List machine learning models.
        """
        return self._list(request)

    def retrieve(self, request, pk=None):
        """
        Get information about a particular machine learning model.
        """
        return self._retrieve(request, pk)
        # obj = self.get_object()
        # logger.info("Retrieve of %s invoked by %s", obj, request.user)
        # ser = self.get_serializer_class()(obj)
        # logger.info("Using serializer class:  %s", type(ser).__name__)
        # return Response(ser.data)

    def destroy(self, request, pk=None):
        """
        Destroy (delete) a machine learning model.
        """
        return self._destroy(request, pk)

    @action(
        detail=True,
        methods=["GET", "PATCH"],
        serializer_class=PermissionsSerializer
    )
    def permissions(self, request, pk=None):
        return self._permissions(request, pk)
    
