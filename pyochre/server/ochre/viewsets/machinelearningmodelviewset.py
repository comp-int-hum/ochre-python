import logging
from rest_framework.decorators import action
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import MachineLearningModelSerializer
from pyochre.server.ochre.models import MachineLearningModel


logger = logging.getLogger(__name__)


class MachineLearningModelViewSet(OchreViewSet):
    serializer_class = MachineLearningModelSerializer
    model = MachineLearningModel
    schema = AutoSchema(
        tags=["machinelearningmodel"],
        component_name="machinelearningmodel",
        operation_id_base="machinelearningmodel"
    )
    accordion_header_template_name = None

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        obj = MachineLearningModel.objects.get(id=pk)
        res = obj.apply(**request.FILES)
        return Response(res)
