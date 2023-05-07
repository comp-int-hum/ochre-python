import logging
from rest_framework.serializers import ModelSerializer, HiddenField, HyperlinkedIdentityField, CurrentUserDefault, CharField, HyperlinkedRelatedField
from pyochre.server.ochre.fields import VegaField, ActionOrInterfaceField, AnnotatedObjectField, AnnotationInteractionField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import Annotation, MachineLearningModel, Query, PrimarySource
from pyochre.server.ochre.vega import  TemporalEvolution, SpatialDistribution, WordCloud



logger = logging.getLogger(__name__)


class AnnotationInteractiveSerializer(OchreSerializer):
    machinelearningmodel = HyperlinkedRelatedField(
        #queryset=MachineLearningModel.objects.all(),
        view_name="api:machinelearningmodel-detail",
        read_only=True,
        allow_null=True,
        style={}
    )
    
    #query = HyperlinkedRelatedField(
    #    queryset=Query.objects.all(),
    #    view_name="api:query-detail",
    #    write_only=True,
    #    allow_null=True
    #)
    primarysource = HyperlinkedRelatedField(
        view_name="api:primarysource-detail",
        read_only=True,
        allow_null=True
    )
    interaction = AnnotationInteractionField(
        view_name="api:annotation-interaction",        
    )
    class Meta:
        model = Annotation
        fields = [
            "machinelearningmodel",
            "primarysource",
            "interaction",
            "name",
            "created_by",
            "url",
            "id"
        ]
