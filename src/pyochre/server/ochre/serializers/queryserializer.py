import logging
from rest_framework.serializers import HyperlinkedIdentityField, CharField, FileField
from pyochre.server.ochre.models import Query
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


class QuerySerializer(OchreSerializer):

    sparql_file = FileField(
        write_only=True
    )

    sparql = CharField(
        read_only=True
    )
    
    class Meta:
        model = Query
        fields = [
            "name",
            "sparql_file",
            "sparql",
            "created_by",
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
