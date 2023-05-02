import os.path
import logging
import tempfile
from rest_framework.serializers import HyperlinkedIdentityField, FileField, BooleanField
from django.conf import settings
from pyochre.server.ochre.models import PrimarySource, Query, Annotation
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.tasks import expand_primarysource


logger = logging.getLogger(__name__)


class HathiTrustSerializer(OchreSerializer):    

    collection_file = FileField(
        write_only=True,
        help_text="A collection CSV file downloaded from the HathiTrust interface"
    )
    class Meta:
        model = PrimarySource
        fields = [
            "name",
            "collection_file",
            "id",
            "url",
        ]
