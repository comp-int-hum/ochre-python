import logging
from rest_framework.serializers import HyperlinkedIdentityField
from pyochre.server.ochre.fields import ActionOrInterfaceField, SparqlEditorField, TabularResultsField
from pyochre.server.ochre.models import Query
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


class QueryInteractiveSerializer(OchreSerializer):

    sparql = SparqlEditorField(
        initial="",
        language="sparql",
        property_field=None,
        allow_blank=True,
        required=False,
        endpoint="sparql",
        nested_parent_field="primary_source"
    )

    perform_url = HyperlinkedIdentityField(
        view_name="api:query-perform",
    )
    
    class Meta:
        model = Query
        fields = [
            "name",
            "sparql",
            "perform_url",
            "created_by",
            "url",
            "id"
        ]
