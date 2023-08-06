import logging
from rest_framework.serializers import CharField, ValidationError, BooleanField
from pyochre.server.ochre.models import Query
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import MonacoEditorField


logger = logging.getLogger(__name__)


class QueryFromTextSerializer(OchreSerializer):

    name = CharField(
        help_text="The name must be unique among queries owned by this user."
    )

    sparql = MonacoEditorField(
        label="SPARQL query",
        help_text="Queries will automatically have the appropriate 'ochre:' prefix added.",
        language="sparql"
    )

    force = BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
        default=False,
        help_text="Overwrite any existing model of the same name and creator"
    )
    
    class Meta:
        model = Query
        fields = [
            "name",
            "sparql",
            "force",
            "created_by"
        ]

    def create(self, validated_data):
        if validated_data.get("force", False):
            for existing in Query.objects.filter(
                    name=validated_data["name"],
                    created_by=validated_data["created_by"]
            ):
                existing.delete()
        query = Query(
            created_by=validated_data["created_by"],
            name=validated_data["name"],
            sparql=validated_data["sparql"]
        )
        query.save()
        return query
