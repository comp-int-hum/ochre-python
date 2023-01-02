import logging
from pyochre.server.ochre.fields import VegaField, ActionOrInterfaceField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import Annotation
from pyochre.server.ochre.vega import  TemporalEvolution, SpatialDistribution, WordCloud


logger = logging.getLogger(__name__)


class AnnotationSerializer(OchreSerializer):
    temporal = ActionOrInterfaceField(
        VegaField(
            vega_class=TemporalEvolution,
            property_field="data",
            allow_null=True,
            read_only=True,
            title="Temporal evolution"
        ),
        title="Temporal evolution",
        view_name="api:annotation-data"
    )
    spatial = ActionOrInterfaceField(
        VegaField(
            vega_class=SpatialDistribution,
            property_field="data",
            allow_null=True,
            read_only=True,
            title="Spatial distribution"            
        ),
        title="Spatial distribution",
        view_name="api:annotation-data"        
    )
    
    class Meta:
        model = Annotation
        fields = [
            "temporal",
            "spatial",
            "name",
            "source_type",
            "source_id",
            "created_by",
            "url",
            "id"
        ]
