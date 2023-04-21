import logging
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import ActionOrInterfaceField
from pyochre.server.ochre.models import MachineLearningModel
from pyochre.server.ochre.fields import MachineLearningModelInteractionField


logger = logging.getLogger(__name__)


class MachineLearningModelInteractiveSerializer(OchreSerializer):
    apply_url = MachineLearningModelInteractionField(
        view_name="api:machinelearningmodel-apply",
    )
    class Meta:
        model = MachineLearningModel
        fields = [
            "name",
            "url",
            "created_by",
            "id",
            "apply_url",
        ]
        
    def create(self, validated_data):
        obj = MachineLearningModel(
            name=validated_data["name"],
            created_by=validated_data["created_by"],
        )        
        obj.save(**validated_data)
        return obj

    def update(self, instance, validated_data):
        instance = super(
            MachineLearningModelInteractiveSerializer,
            self
        ).update(
            instance,
            validated_data
        )
        instance.save(**validated_data)
        return instance
