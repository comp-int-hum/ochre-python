import logging
from rest_framework.serializers import CharField, FileField, BooleanField, ValidationError
from pyochre.server.ochre.models import Query
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


class QueryFromFileSerializer(OchreSerializer):

    name = CharField(
        help_text="Names must be unique for the user and type of object."
    )

    sparql_file = FileField(
        write_only=True,
        help_text="A text file with a SPARQL SELECT query that shouldn't declare, but may use, the 'ochre:' prefix.  The query should not make reference to any particular graph (OCHRE handles that).",
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
            "sparql_file",
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
        obj = Query(
            name=validated_data["name"],
            created_by=validated_data["created_by"],
            sparql=validated_data["sparql_file"].read().decode("utf-8")
        )
        obj.save()
        return obj
