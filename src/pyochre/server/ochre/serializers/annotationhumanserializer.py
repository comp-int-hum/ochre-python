import logging
from rest_framework.serializers import ModelSerializer, HiddenField, HyperlinkedIdentityField, CurrentUserDefault, CharField, HyperlinkedRelatedField
from pyochre.server.ochre.fields import VegaField, ActionOrInterfaceField, AnnotatedObjectField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import Annotation, Query, PrimarySource, User
from pyochre.server.ochre.vega import  TemporalEvolution, SpatialDistribution, WordCloud



logger = logging.getLogger(__name__)


class AnnotationHumanSerializer(OchreSerializer):

    query = HyperlinkedRelatedField(
        queryset=Query.objects.all(),
        view_name="api:query-detail",
        required=False
    )
    
    primarysource = HyperlinkedRelatedField(
        queryset=PrimarySource.objects.all(),
        view_name="api:primarysource-detail",
    )

    user = HyperlinkedRelatedField(
        queryset=User.objects.all(),
        view_name="api:user-detail"
    )
    
    class Meta:
        model = Annotation
        exclude = ["machinelearningmodel"]

    def create(self, validated_data):
        obj = Annotation(
           name=validated_data["name"],
           created_by=validated_data["created_by"],
        )
        obj.save()
        return obj
