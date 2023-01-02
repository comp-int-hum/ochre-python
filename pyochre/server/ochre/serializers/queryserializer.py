import logging
from pyochre.server.ochre.fields import ActionOrInterfaceField, SparqlEditorField, TabularResultsField
from pyochre.server.ochre.models import Query
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


example_query = """
PREFIX ochre: <urn:ochre:>
PREFIX so: <https://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?title (SAMPLE(?m) as ?mid) (SAMPLE(?p) as ?pub_date) (SAMPLE(?l) as ?lang)
WHERE {{
  ?text so:creator ?author .
  ?author so:familyName ?last_name .
  ?author so:givenName ?first_name .
  ?text so:name ?title .
  ?text ochre:materialId ?m .
  ?text so:datePublished ?p .
  ?text so:inLanguage ?l .
  FILTER (?p > "1700-01-01"^^xsd:date && ?p < "1900-01-01"^^xsd:date)
}} GROUP BY ?author ?title
"""


class QuerySerializer(OchreSerializer):
    sparql = SparqlEditorField(
        initial=example_query,
        language="sparql",
        property_field=None,
        allow_blank=True,
        required=False,
        endpoint="sparql",
        nested_parent_field="primary_source"
    )
    perform_url = ActionOrInterfaceField(
        TabularResultsField(
            property_field="perform",
            property_field_args={"limit" : 10},
            column_names_path="head.vars",
            lookup_path="head.vars",
            rows_path="results.bindings",
            value_format="{0[value]}",
        ),
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
