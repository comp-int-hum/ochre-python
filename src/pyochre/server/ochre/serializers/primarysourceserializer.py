import logging
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import ActionOrInterfaceField
from pyochre.server.ochre.models import PrimarySource
from pyochre.server.ochre.fields import PrimarySourceInteractionField


logger = logging.getLogger(__name__)


class PrimarySourceSerializer(OchreSerializer):
    domain = PrimarySourceInteractionField(
    )
    class Meta:
        model = PrimarySource
        fields = [
            "name",
            "url",
            "creator",
            "id",
            "domain",
        ]
        
    def update(self, instance, validated_data):
        instance = super(
            PrimarySourceSerializer,
            self
        ).update(
            instance,
            validated_data
        )
        instance.save(**validated_data)
        return instance
