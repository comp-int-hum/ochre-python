import logging
from django.db.models import TextField
from django.conf import settings
from pyochre.server.ochre.models import OchreModel
from pyochre.utils import rdf_store


logger = logging.getLogger(__name__)


class Query(OchreModel):
    class Meta(OchreModel.Meta):
        verbose_name_plural = "Queries"
    sparql = TextField()
        

    #def save(self, *argv, **argd):
    #    print(argv, argd)
    #def __str__(self):
    #    return self.name

    #def perform(self, limit=None, offset=None):
    #    store = rdf_store(settings=settings)
    #    ds = rdflib.Dataset(store=store)
    #    return ds.query(query.getlist("query")[0])
