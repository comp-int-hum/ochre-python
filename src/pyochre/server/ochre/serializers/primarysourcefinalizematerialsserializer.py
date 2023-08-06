import logging
from rest_framework.serializers import ModelSerializer
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import PrimarySource


logger = logging.getLogger(__name__)


class PrimarySourceFinalizeMaterialsSerializer(ModelSerializer):

    class Meta:
        model = PrimarySource
        fields = [
            "id",
        ]
