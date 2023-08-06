import logging
from pyochre.server.ochre.models import Query
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import MonacoEditorField


logger = logging.getLogger(__name__)


class QueryInteractiveSerializer(OchreSerializer):

    sparql = MonacoEditorField(
        label="SPARQL",
        language="sparql",
        style={
            "hide_label" : True
        }
    )

    class Meta:
        model = Query
        fields = [
            "name",
            "sparql",
        ]
