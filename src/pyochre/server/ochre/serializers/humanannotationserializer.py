import logging
from rest_framework.serializers import ModelSerializer, HiddenField, HyperlinkedIdentityField, CurrentUserDefault, CharField, HyperlinkedRelatedField
from pyochre.server.ochre.fields import VegaField, ActionOrInterfaceField, AnnotatedObjectField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import Annotation, Query, PrimarySource, User
from pyochre.server.ochre.vega import  TemporalEvolution, SpatialDistribution, WordCloud
from pyochre.server.ochre import tasks


logger = logging.getLogger(__name__)


class HumanAnnotationSerializer(OchreSerializer):

    query = HyperlinkedRelatedField(
        queryset=Query.objects.all(),
        view_name="api:query-detail",
        #many=True,
        required=False
    )
    
    primarysource = HyperlinkedRelatedField(
        queryset=PrimarySource.objects.all(),
        view_name="api:primarysource-detail",
        #many=True
    )

    user = HyperlinkedRelatedField(
        queryset=User.objects.all(),
        view_name="api:user-detail"
    )
    
    class Meta:
        model = Annotation
        fields = [
            "query",
            "primarysource",
            "user",
            "name",
            "created_by",
            "url",
            "id"
        ]

    def create(self, validated_data):
        obj = Annotation(
           name=validated_data["name"],
           created_by=validated_data["created_by"],
        )
        obj.save()
        return obj
