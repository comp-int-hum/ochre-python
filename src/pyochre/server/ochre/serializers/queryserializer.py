import logging
from rest_framework.serializers import HyperlinkedIdentityField, CharField, FileField, CurrentUserDefault, BaseSerializer, HiddenField, Serializer
from pyochre.server.ochre.models import Query
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import MonacoEditorField


logger = logging.getLogger(__name__)


class QuerySerializer(OchreSerializer):
    url = HyperlinkedIdentityField(
        view_name="api:query-detail",
        lookup_field="id",
        lookup_url_kwarg="pk",
        read_only=True,
        help_text="URL of this query."
    )
    name = CharField(
        help_text="Names must be unique for the user and type of object."
    )
    sparql = MonacoEditorField(
        label="SPARQL query",
        help_text="Queries will automatically have the appropriate 'ochre:' prefix added."
    )
    permissions_url = HyperlinkedIdentityField(
        view_name="api:query-permissions"
    )
    created_by = HiddenField(            
        default=CurrentUserDefault()
    )
    
    class Meta:
        model = Query
        fields = [
            "name",
            "sparql",            
            "url",
            "permissions_url",
            "id"
        ]

    def create(self, validated_data):        
        obj = Query(
            name=validated_data["name"],
            created_by=validated_data["created_by"],
            sparql=validated_data["sparql"] #.read().decode("utf-8")
        )
        obj.save()
        return obj
