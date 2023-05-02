import logging
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField, IntegerField, HyperlinkedRelatedField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import ActionOrInterfaceField
from pyochre.server.ochre.models import MachineLearningModel
from pyochre.server.ochre.fields import MachineLearningModelInteractionField
from pyochre.server.ochre.tasks import apply_machinelearningmodel, train_topic_model, import_huggingface_model

logger = logging.getLogger(__name__)


class MachineLearningModelSerializer(OchreSerializer):
    #huggingface_name = CharField(
    #    required=False,
    #    write_only=True
    #)

    #topic_count = IntegerField(
    #    required=False,
    #    write_only=True
    #)
    
    #stopwords = CharField(
    #    required=False,
    #    write_only=True
    #)

    #mar_file = FileField(
    #    required=False,
    #    write_only=True
    #)
    #mar_url = URLField(
    #    required=False,
    #    write_only=True
    #)

    #signature_file = FileField(
    #    required=False,
    #    write_only=True
    #)
    #signature_url = URLField(
    #    required=False,
    #    write_only=True
    #)
#    apply_url = HyperlinkedIdentityField(
#        view_name="api:machinelearningmodel-apply",
#    )

    #query = IntegerField(
    #    required=False,
    #    write_only=True
    #)
    #primarysource = IntegerField(
    #    required=False,
    #    write_only=True
    #)    
    class Meta:
        model = MachineLearningModel
        fields = [
            "name",
            #"query",
            #"primarysource",
            #"signature_file",
            #"mar_file",
            #"huggingface_name",
            #"topic_count",
            "url",
            "created_by",
            "id",
            #"apply_url",
            #"mar_url",
            #"signature_url",
            #"stopwords"
        ]
        
    def create(self, validated_data):
        obj = MachineLearningModel(
            name=validated_data["name"],
            created_by=validated_data["created_by"],
        )
        return self.update(obj, validated_data)

    def update(self, instance, validated_data):
        instance = super(
            MachineLearningModelSerializer,
            self
        ).update(
            instance,
            validated_data
        )
        if "huggingface_name" in validated_data:
            import_huggingface_model.delay(
                validated_data["name"],
                validated_data["created_by"].id,
                validated_data["huggingface_name"]
            )
        elif "mar_file" in validated_data:
            pass
        elif "topic_count" in validated_data:
            train_topic_model.delay(
                validated_data["name"],
                validated_data["created_by"].id,
                validated_data.get("query"),
                validated_data.get("primarysource"),
                lowercase=validated_data.get("lowercase", True),
                topic_count=validated_data.get("topic_count", 10),
                stopwords=validated_data.get("stopwords", [])
            )

            pass
        else:
            pass # starcoder

        instance.save(**validated_data)
        return instance
