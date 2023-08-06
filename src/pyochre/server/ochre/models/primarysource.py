import os.path
import io
import logging
import json
from importlib.resources import files
from django.db.models import UniqueConstraint
from django.conf import settings
from rdflib import Graph, Dataset
from rdflib.query import Result
from rdflib.plugins.sparql import prepareQuery
import requests
from pyochre.server.ochre.models import OchreModel, User, AsyncMixin
from pyochre.utils import rdf_store, ochrequery as OQ, ochreturtle as OT
from pyochre.primary_sources import create_domain


logger = logging.getLogger(__name__)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


@shared_task
def clear_graphs(*uris):
    for uri in uris:
        resp = requests.delete(
            os.path.join(settings.JENA_URL, "ochre", "data"),
            params={
                "graph" : uri
            },
            auth=(settings.JENA_USER, settings.JENA_PASSWORD)
        )
        logger.info("Deleting graph '%s' gave status '%s'", uri, resp.status_code)


class PrimarySource(AsyncMixin, OchreModel):

    class Meta(OchreModel.Meta):
        pass
    
    def sparql_query_endpoint(self):
        return "{}/primarysource_{}/query".format(settings.JENA_URL, self.id)

    def sparql_update_endpoint(self):
        return "{}/primarysource_{}/update".format(settings.JENA_URL, self.id)

    def construct_query(self, q):
        resp = requests.post(
            os.path.join(settings.JENA_URL, "ochre", "query"),
            data=q,
            headers={
                "Content-Type" : "application/sparql-query",
                "Accept" : "application/rdf+xml",
                "charset" : "utf-8"
            },
            params={"default-graph-uri" : [self.data_uri, self.domain_uri, "default"]}
        )
        g = Graph()
        g.parse(data=resp.content.decode("utf-8"), format="xml")
        return g

    def select_query(self, q):
        resp = requests.post(
            os.path.join(settings.JENA_URL, "ochre", "query"),
            data=q,
            headers={
                "Content-Type" : "application/sparql-query",
                "Accept" : "application/sparql-results+xml",
                "charset" : "utf-8"
            },
            params={"default-graph-uri" : [self.data_uri, self.domain_uri, "default"]}
        )
        return Result.parse(
            source=io.StringIO(
                resp.content.decode("utf-8")
            )
        )

    def query(self, q):
        q = OQ(q)
        n = prepareQuery(q).algebra.name
        if n == "SelectQuery":
            return self.select_query(q)
        elif n == "ConstructQuery":
            return self.construct_query(q)

    def update(self, q):
        # HACK
        q = "WITH <{}>".format(self.data_uri) + q
        q = OQ(q)
        resp = requests.post(
            os.path.join(settings.JENA_URL, "ochre", "update"),
            data=q,
            headers={
                "Content-Type" : "application/sparql-update",
                "charset" : "utf-8"
            },
            params={
            },
            auth=(settings.JENA_USER, settings.JENA_PASSWORD)
        )
        return resp
    
    @property
    def domain_uri(self):
        return "{}{}_domain".format(settings.OCHRE_NAMESPACE, self.id)
    
    @property
    def domain(self):
        resp = requests.get(
            "{}/ochre/data".format(settings.JENA_URL),
            params={"graph" : self.domain_uri},
            headers={"Accept" : "text/turtle", "charset" : "utf-8"}
        )
        g = Graph()
        g.parse(data=resp.content, format="turtle")
        return g
        
    @property
    def data_uri(self):
        return "{}{}_data".format(settings.OCHRE_NAMESPACE, self.id)

    @property
    def data(self, limit=None):
        resp = requests.get(
            "{}/ochre/data".format(settings.JENA_URL),
            params={"graph" : self.data_uri},
            headers={"Accept" : "text/turtle", "charset" : "utf-8"}
        )
        g = Graph()
        g.parse(data=resp.content, format="turtle")
        return g

    def delete(self, **argd):
        uris = [self.data_uri, self.domain_uri]
        clear_graphs.delay(*uris)
        return super(PrimarySource, self).delete(**argd)

    def add(self, graph):
        with open("test.rdf", "wb") as ofd:
            ofd.write(graph)
        resp = requests.post(
            os.path.join(settings.JENA_URL, "ochre", "data"),
            data=graph if isinstance(graph, bytes) else graph.serialize(format="xml").encode("utf-8"),
            headers={
                "Content-Type" : "application/rdf+xml",
                "charset" : "utf-8"
            },
            params={
                "graph" : self.data_uri
            },
            auth=(settings.JENA_USER, settings.JENA_PASSWORD)
        )
        return resp

    def infer_domain(self):
        domain_query = files("pyochre").joinpath("data/domain_query.sparql").read_text()
        resp = requests.put(
            os.path.join(settings.JENA_URL, "ochre", "data"),
            data=create_domain(self).serialize(format="turtle"),
            headers={
                "Content-Type" : "text/turtle",
                "charset" : "utf-8"
            },
            params={
                "graph" : self.domain_uri
            },
            auth=(settings.JENA_USER, settings.JENA_PASSWORD)
        )
        self.save()
        return resp
