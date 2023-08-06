import logging
from rest_framework.serializers import ModelSerializer, HiddenField, HyperlinkedIdentityField, CurrentUserDefault, CharField, HyperlinkedRelatedField, BooleanField
from pyochre.server.ochre.fields import VegaField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import Annotation, Query, PrimarySource, User
from pyochre.server.ochre.vega import  TemporalEvolution, SpatialDistribution, WordCloud


logger = logging.getLogger(__name__)


class AnnotationHumanSerializer(OchreSerializer):
    
    name = CharField(
        max_length=2000,
        required=False,
        label="Name",
        help_text="Names must be unique for the user and type of object.",
    )

    user = HyperlinkedRelatedField(
        queryset=User.objects.exclude(username="AnonymousUser"),
        view_name="api:user-detail",
        help_text="The user who will perform this annotation."
    )

    primarysource = HyperlinkedRelatedField(
        queryset=PrimarySource.objects.all(),
        view_name="api:primarysource-detail",
        help_text="The primary source this annotation will provide information about."
    )
    
    query = HyperlinkedRelatedField(
        queryset=Query.objects.all(),
        view_name="api:query-detail",
        required=False,
        help_text="An optional query to sub-select or rearrange the primary source."
    )
    force = BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
        default=False,
        help_text="Overwrite any existing annotation of the same name and creator."
    )
    
    class Meta:
        model = Annotation
        exclude = ["machinelearningmodel"]

    def create(self, validated_data):
        if validated_data.get("force", False):
            for existing in Annotation.objects.filter(
                    name=validated_data["name"],
                    created_by=validated_data["created_by"]
            ):
                existing.delete()        
        obj = Annotation(
            name=validated_data["name"],
            created_by=validated_data["created_by"],
            primarysource=validated_data["primarysource"],
            query=validated_data["query"],
            user=validated_data["user"]
        )
        obj.save()
        return obj
