import logging
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField, ListField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import PrimarySource


logger = logging.getLogger(__name__)


class PrimarySourceMaterialsSerializer(OchreSerializer):

    name = CharField(
        required=True,
        help_text="Name of material file being created"
    )

    file = FileField(
        required=True,
        help_text="File whose contents will correspond to the name, in this primary source"
    )
    
    class Meta:
        model = PrimarySource
        fields = [
            "name",
            "file",
            "id",
        ]
