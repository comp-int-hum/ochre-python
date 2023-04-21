import logging
from rest_framework.serializers import HyperlinkedIdentityField
from pyochre.server.ochre.models import PrimarySource, Query, Annotation
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


class PrimarySourceSerializer(OchreSerializer):    

    domain_url = HyperlinkedIdentityField(
        view_name="api:primarysource-domain"
    )
    
    clear_url = HyperlinkedIdentityField(
        view_name="api:primarysource-clear"
    )
    
    query_url = HyperlinkedIdentityField(
        view_name="api:primarysource-query"
    )
    
    update_url = HyperlinkedIdentityField(
        view_name="api:primarysource-sparqlupdate"
    )    
    
    class Meta:
        model = PrimarySource
        fields = [
            "name",
            "domain_url",
            "creator",
            "id",
            "url",
            "clear_url",
            "query_url",
            "update_url"
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
    
