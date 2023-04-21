import logging
from rest_framework.serializers import HyperlinkedIdentityField, CharField
from pyochre.server.ochre.models import Query
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


class QuerySerializer(OchreSerializer):

    sparql = CharField()

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
