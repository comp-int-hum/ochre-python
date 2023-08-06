import logging
from rest_framework.serializers import HyperlinkedIdentityField, CharField, FileField, Serializer, HiddenField, CurrentUserDefault
from pyochre.server.ochre.models import Query
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


class QueryUploadSerializer(Serializer):
    name = CharField(
        help_text="Names must be unique for the user and type of object."
    )
    sparql_file = FileField(
        write_only=True,
        help_text="A text file with a SPARQL SELECT query that shouldn't declare, but may use, the 'ochre:' prefix.  The query should not make reference to any particular graph (OCHRE handles that).",
    )
    created_by = HiddenField(            
        default=CurrentUserDefault()
    )
    
    class Meta:
        model = Query
        fields = [
            "name",
            "sparql_file",
            "creator",
            "url",
            "id"
        ]

    def create(self, validated_data):        
        obj = Query(
            name=validated_data["name"],
            created_by=validated_data["created_by"],
            sparql=validated_data["sparql_file"].read().decode("utf-8")
        )
        obj.save()
        return obj
