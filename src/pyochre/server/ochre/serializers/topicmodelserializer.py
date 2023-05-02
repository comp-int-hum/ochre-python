import logging
from rest_framework.serializers import CharField, IntegerField, HyperlinkedRelatedField, ListField, FloatField, BooleanField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import ActionOrInterfaceField
from pyochre.server.ochre.models import MachineLearningModel, Query, PrimarySource
from pyochre.server.ochre.fields import MachineLearningModelInteractionField
from pyochre.server.ochre.tasks import train_topic_model


logger = logging.getLogger(__name__)


class TopicModelSerializer(OchreSerializer):
    primarysource = HyperlinkedRelatedField(
        queryset=PrimarySource.objects.all(),
        view_name="api:primarysource-detail",
    )
    query = HyperlinkedRelatedField(
        queryset=Query.objects.all(),
        view_name="api:query-detail",
        allow_null=True,
        required=False
    )    
    topic_count = IntegerField(
        required=False,
        write_only=True,
        default=10,
        allow_null=True,
        help_text="The number of topics the model will infer"
    )
    stopwords = ListField(
        child=CharField(
            required=False,
            write_only=True,
            help_text="A list of words to ignore"
        ),
        default=[],
        allow_null=True,
        required=False
    )
    random_seed = IntegerField(
        required=False,
        write_only=True,
        default=0,
        allow_null=True,
        help_text="Seed for random number generator"
    )
    maximum_documents = IntegerField(
        required=False,
        write_only=True,
        allow_null=True,
        help_text="Maximum number of documents to train on"
    )
    passes = IntegerField(
        required=False,
        write_only=True,
        default=100,
        allow_null=True,
        help_text="Number of training passes over corpus"
    )
    iterations = IntegerField(
        required=False,
        write_only=True,
        default=100,
        allow_null=True,
        help_text="Number of iterations for variational optimization"
    )
    maximum_context_tokens = IntegerField(
        required=False,
        write_only=True,
        allow_null=True,
        default=500,
        help_text="Maximum size of a 'context' in tokens"
    )
    lowercase = BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
        default=False,
        help_text="Whether to lower-case data"
    )
    minimum_token_length = IntegerField(
        required=False,
        write_only=True,
        default=3,
        allow_null=True,
        help_text="Number of iterations for variational optimization"
    )
    maximum_vocabulary_size = IntegerField(
        required=False,
        write_only=True,
        default=30000,
        allow_null=True,
        help_text="Number of iterations for variational optimization"
    )
    minimum_occurrence = IntegerField(
        required=False,
        write_only=True,
        default=5,
        allow_null=True,
        help_text="Number of iterations for variational optimization"
    )
    maximum_proportion = FloatField(
        required=False,
        write_only=True,
        default=0.5,
        allow_null=True,
        help_text="Number of iterations for variational optimization"
    )
    class Meta:
        model = MachineLearningModel
        fields = [
            "name",
            "primarysource",
            "query",
            "topic_count",
            "url",
            "created_by",
            "id",
            "stopwords",
            "random_seed",
            "maximum_documents",
            "passes",
            "iterations",
            "lowercase",
            "maximum_context_tokens",
            "minimum_token_length",
            "maximum_vocabulary_size",
            "maximum_proportion",
            "minimum_occurrence"
        ]
