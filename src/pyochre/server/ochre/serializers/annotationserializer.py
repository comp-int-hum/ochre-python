import logging
from rest_framework.serializers import ModelSerializer, HiddenField, HyperlinkedIdentityField, CurrentUserDefault, CharField, HyperlinkedRelatedField
from pyochre.server.ochre.fields import VegaField, ActionOrInterfaceField, AnnotatedObjectField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import Annotation, MachineLearningModel, Query, PrimarySource
from pyochre.server.ochre.vega import  TemporalEvolution, SpatialDistribution, WordCloud
from pyochre.server.ochre import tasks


logger = logging.getLogger(__name__)


class AnnotationSerializer(OchreSerializer):
    # temporal = ActionOrInterfaceField(
    #     VegaField(
    #         vega_class=TemporalEvolution,
    #         property_field="data",
    #         allow_null=True,
    #         read_only=True,
    #         title="Temporal evolution"
    #     ),
    #     title="Temporal evolution",
    #     view_name="api:annotation-data"
    # )
    # spatial = ActionOrInterfaceField(
    #     VegaField(
    #         vega_class=SpatialDistribution,
    #         property_field="data",
    #         allow_null=True,
    #         read_only=True,
    #         title="Spatial distribution"            
    #     ),
    #     title="Spatial distribution",
    #     view_name="api:annotation-data"        
    # )
    #source_object = AnnotatedObjectField(read_only=True)
    # machinelearningmodel = HyperlinkedRelatedField(
    #    queryset=MachineLearningModel.objects.all(),
    #    view_name="api:machinelearningmodel-detail",
    #    write_only=True,
    #    allow_null=True
    # )
    #query = HyperlinkedRelatedField(
    #    queryset=Query.objects.all(),
    #    view_name="api:query-detail",
    #    write_only=True,
    #    allow_null=True
    #)
    #primarysource = HyperlinkedRelatedField(
    #    queryset=PrimarySource.objects.all(),
    #    view_name="api:primarysource-detail",
    #    write_only=True,
    #    allow_null=True
    #)
    class Meta:
        model = Annotation
        fields = [
            "machinelearningmodel",
            #"query",
            #"primarysource",
            #"temporal",
            #"spatial",
            "name",
            #"source_object",
            #"source_type",
            #"source_id",
            "created_by",
            "url",
            "id"
        ]

    def create(self, validated_data):
        obj = Annotation(
           name=validated_data["name"],
           created_by=validated_data["created_by"],
        )
        obj.save() #**validated_data)
        tasks.apply_machinelearningmodel.delay(
            obj.id,
            validated_data["machinelearningmodel"].id,
            validated_data["primarysource"].id,
            #validated_data["query"].id
        )
        return obj
        
    def update(self, instance, validated_data):
        instance = super(
            AnnotationSerializer,
            self
        ).update(
            instance,
            validated_data
        )
        instance.save(**validated_data)
        tasks.apply_machinelearningmodel.delay(
            instance.id,
            validated_data["machinelearningmodel"].id,
            validated_data["primarysource"].id,
            #validated_data["query"].id
        )
        return instance
