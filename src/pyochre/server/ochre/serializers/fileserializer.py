import logging
from rest_framework.serializers import HyperlinkedIdentityField
from pyochre.server.ochre.models import File
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)

    
class FileSerializer(OchreSerializer):
    url = HyperlinkedIdentityField(
        view_name="api:file-detail",
        lookup_field="id",
        lookup_url_kwarg="pk",
        read_only=True,
        help_text="URL of this file."
    )
    class Meta(OchreSerializer.Meta):
        model = File
        fields = [            
            f.name for f in File._meta.fields
        ] + OchreSerializer.Meta.fields
