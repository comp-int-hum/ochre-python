import logging
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action


logger = logging.getLogger(__name__)


class ServiceViewSet(ViewSet):
    schema = AutoSchema(
        tags=["service"],
        component_name="service",
        operation_id_base="service"
    )

    @action(detail=True, methods=["get"])
    def markdown(self, request, pk=None):
        return Response()
        #obj = MachineLearningModel.objects.get(id=pk)
        #res = obj.apply(**request.FILES, **request.data)
        #return Response(res)
