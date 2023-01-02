import logging
from rest_framework.serializers import HyperlinkedIdentityField
from pyochre.server.ochre.models import PrimarySource, Query, Annotation
from pyochre.server.ochre.fields import VegaField, ActionOrInterfaceField
from pyochre.server.ochre.vega import PrimarySourceDomainGraph, PrimarySourceDataGraph
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


class PrimarySourceSerializer(OchreSerializer):    
    domain_url = ActionOrInterfaceField(
        VegaField(
            vega_class=PrimarySourceDomainGraph,
            property_field="domain"
        ),
        view_name="api:primarysource-domain",
        title="Domain"
    )
    clear_url = HyperlinkedIdentityField(
        view_name="api:primarysource-clear"
    )
    sparql_query_url = HyperlinkedIdentityField(
        view_name="api:primarysource-sparqlquery"
    )
    sparql_update_url = HyperlinkedIdentityField(
        view_name="api:primarysource-sparqlupdate"
    )    
    # data_url = ActionOrInterfaceField(
    #    VegaField(
    #        vega_class=PrimarySourceDataGraph,
    #        property_field="data",
    #        #property_field_args={"limit" : 10}
    #    ),
    #    view_name="api:primarysource-data",
    #    title="Data"
    # )
    
    class Meta:
        model = PrimarySource
        fields = [
            "name",
            "domain_url",
            "creator",
            "id",
            "url",
            "clear_url",
            "sparql_query_url",
            "sparql_update_url"
        ]

    def create(self, validated_data):
        logger.info("Creating new primarysource")
        obj = PrimarySource(
            name=validated_data["name"],
            created_by=validated_data["created_by"]
        )
        obj.save(**validated_data)
        return obj

    def update(self, instance, validated_data):
        super(
            PrimarySourceSerializer,
            self
        ).update(
            instance,
            validated_data
        )
        instance.save(**validated_data)
        return instance
