import logging
from django.db.models import TextField
from django.conf import settings
from pyochre.server.ochre.models import OchreModel
from pyochre.utils import rdf_store


logger = logging.getLogger(__name__)


class Query(OchreModel):

    class Meta(OchreModel.Meta):
        verbose_name_plural = "queries"        

    sparql = TextField()
