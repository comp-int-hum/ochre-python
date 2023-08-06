import logging
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField, HiddenField, IntegerField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import PrimarySource
from pyochre.server.ochre.fields import VegaField


logger = logging.getLogger(__name__)


class PrimarySourceInteractiveSerializer(OchreSerializer):
    domain = VegaField(
        label="Domain structure",
        view_name="api:primarysource-domain",
        vega_class_name="PrimarySourceDomainGraph"
    )
    class Meta:
        model = PrimarySource
        fields = [
            "domain",
        ]
