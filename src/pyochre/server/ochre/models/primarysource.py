import logging
import json
from django.conf import settings
import rdflib
from rdflib.plugins.sparql import prepareQuery
from pyochre.server.ochre.models import OchreModel, User, AsyncMixin
from pyochre.utils import rdf_store


logger = logging.getLogger(__name__)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func

    
class PrimarySource(AsyncMixin, OchreModel):

    def update(self, update):
        store = rdf_store(settings=settings)
        store.update(update.decode("utf-8"))
        store.commit()
        return None

    def sparql_query_endpoint(self):
        return "{}/primarysource_{}/query".format(settings.JENA_URL, self.id)

    def sparql_update_endpoint(self):
        return "{}/primarysource_{}/update".format(settings.JENA_URL, self.id)

    def query(self, query):        
        store = rdf_store(
            settings=settings,
            return_format="application/rdf+xml"
        )
        pquery = """PREFIX ochre: <{}>
        {}
        """.format(
            settings.OCHRE_NAMESPACE,
            query
        )
        #pquery = prepareQuery(
        #    query,
        #    initNs={"ochre" : settings.OCHRE_NAMESPACE}
        #)
        return store.query(pquery, queryGraph=self.data_uri)
        
    @property
    def domain(self):
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)
        g = rdflib.Graph()
        for tr in ds.triples((None, None, None, self.domain_uri)):
            g.add(tr)
        return g
        
    @property
    def data_uri(self):
        return "{}{}_data".format(settings.OCHRE_NAMESPACE, self.id)

    @property
    def domain_uri(self):
        return "{}{}_domain".format(settings.OCHRE_NAMESPACE, self.id)

    def clear(self):
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)
        ds.remove_graph(self.data_uri)
        ds.remove_graph(self.domain_uri)
        ds.commit()
        return None

    @property
    def data(self, limit=None):
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)
        g = rdflib.Graph()
        for tr in ds.triples((None, None, None, self.data_uri)):
            g.add(tr)
        return g #.serialize(format="json-ld")

    def delete(self, **argd):
        try:
            self.clear()
        except:
            pass
        return super(PrimarySource, self).delete(**argd)        
    
    def save(
            self,
            domain_file=None,
            annotations_file=None,
            data_file=None,
            materials_file=None,
            limit=None,
            **argd
    ):
        create = not (self.id and True)
        self.state = self.COMPLETE
        retval = super(PrimarySource, self).save()
        if create:
            store = rdf_store(settings=settings)
            store.update("CREATE GRAPH <{}>".format(self.data_uri))
            store.update("CREATE GRAPH <{}>".format(self.domain_uri))
            store.commit()
        return retval
