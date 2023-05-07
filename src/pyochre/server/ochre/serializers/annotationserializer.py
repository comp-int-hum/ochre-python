import logging
from django.conf import settings
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import Annotation


logger = logging.getLogger(__name__)


class AnnotationSerializer(OchreSerializer):
    class Meta:
        model = Annotation
        fields = [
            "machinelearningmodel",
            "primarysource",
            "user",
            "name",
            "creator",
            "created_by",
            "url",
            "id"
        ]
