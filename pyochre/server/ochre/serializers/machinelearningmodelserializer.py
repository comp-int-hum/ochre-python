import logging
from rest_framework.serializers import FileField, URLField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import ActionOrInterfaceField
from pyochre.server.ochre.models import MachineLearningModel
from pyochre.server.ochre.fields import MachineLearningModelInteractionField


logger = logging.getLogger(__name__)


class MachineLearningModelSerializer(OchreSerializer):
    mar_file = FileField(
        required=False,
        write_only=True
    )
    mar_url = URLField(
        required=False,
        write_only=True
    )
    signature_file = FileField(
        required=False,
        write_only=True
    )
    signature_url = FileField(
        required=False,
        write_only=True
    )
    apply_url = ActionOrInterfaceField(
        MachineLearningModelInteractionField(
            detail_endpoint=True,
            endpoint="api:machinelearningmodel-apply",
            language="torchserve_text",
            property_field="apply"
        ),
        view_name="api:machinelearningmodel-apply",
        title="Interact"
    )

    class Meta:
        model = MachineLearningModel
        fields = [
            "name",
            "signature_file",
            "mar_file",
            "url",
            "created_by",
            "id",
            "apply_url",
            "mar_url",
            "signature_url",            
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
            MachineLearningModelSerializer,
            self
        ).update(
            instance,
            validated_data
        )
        instance.save(**validated_data)
        return instance
