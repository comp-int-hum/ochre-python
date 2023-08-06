import logging
from rest_framework.serializers import HyperlinkedIdentityField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import PrimarySource, User


logger = logging.getLogger(__name__)


class PrimarySourceSerializer(OchreSerializer):
    domain_url = HyperlinkedIdentityField(
        view_name="api:primarysource-domain",
        read_only=True,
        style={"base_template" : "input.html"},
        help_text="URL of the domain graph for this primary source."
    )
    data_url = HyperlinkedIdentityField(
        view_name="api:primarysource-data",
        read_only=True,
        style={"base_template" : "input.html"},
        help_text="URL of the data graph for this primary source."
    )
    url = HyperlinkedIdentityField(
        view_name="api:primarysource-detail",
        lookup_field="id",
        lookup_url_kwarg="pk",
        read_only=True,
        style={"base_template" : "input.html"},
        help_text="URL of this primary source."
    )

    class Meta:
        model = PrimarySource
        fields = [
            "name",
            "url",
            "domain_url",
            "data_url",
            "creator_url",            
        ]
        
    def update(self, instance, validated_data):
        instance = super(
            PrimarySourceSerializer,
            self
        ).update(
            instance,
            validated_data
        )
        instance.save(**validated_data)
        return instance

    def creation_methods(self):
        return [
            {
                "title" : "Create from XSL transformation",
                "url" : "api:primarysource-create_from_xsl_transformation"
            },
            {
                "title" : "Create from HathiTrust collection",
                "url" : "api:primarysource-create_from_hathitrust_collection"
            }
        ]
    
