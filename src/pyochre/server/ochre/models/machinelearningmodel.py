import logging
import json
import io
import os.path
import os
from django.conf import settings
import requests
import rdflib
from rdflib.query import Result
from pyochre.server.ochre.models import OchreModel, AsyncMixin
from pyochre.utils import rdf_store, to_graph, from_graph, ochrequery as OQ
from pyochre.server.ochre.decorators import ochre_cache_method
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, Namespace


logger = logging.getLogger(__name__)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


@shared_task
def clear(pk, uris):
    resp = requests.delete(
        "{}/models/{}".format(
            settings.TORCHSERVE_MANAGEMENT_ADDRESS,
            pk
        )
    )
    model_file = os.path.join(settings.MODELS_ROOT, "{}_model.mar".format(pk))
    if os.path.exists(model_file):
        os.remove(os.path.join(settings.MODELS_ROOT, "{}_model.mar".format(pk)))
    store = rdf_store(settings=settings)
    ds = rdflib.Dataset(store=store)
    for uri in uris:
        ds.remove_graph(uri)
    ds.commit()        
    

class MachineLearningModel(AsyncMixin, OchreModel):

    class Meta(OchreModel.Meta):
        pass

    @property
    def signature_uri(self):
        return "{}{}_model_signature".format(settings.OCHRE_NAMESPACE, self.id)

    def query_signature(self, query):
        resp = requests.post(
            os.path.join(settings.JENA_URL, "ochre", "query"),
            data=OQ(query),
            headers={
                "Content-Type" : "application/sparql-query",
                "Accept" : "application/sparql-results+xml",
                "charset" : "utf-8"
            },
            params={"default-graph-uri" : [self.signature_uri, settings.ONTOLOGY_URI]}
        )
        return Result.parse(
            source=io.StringIO(
                resp.content.decode("utf-8")
            )
        )
    
    @property
    def signature(self, *argv, **argd):
        resp = requests.get(
            "{}/ochre/data".format(settings.JENA_URL),
            params={"graph" : self.signature_uri},
            headers={"Accept" : "text/turtle", "charset" : "utf-8"}
        )
        g = Graph()
        g.parse(data=resp.content, format="turtle")
        return g

    def delete_signature(self):
        resp = requests.delete(
            "{}/ochre/data".format(settings.JENA_URL),
            params={"graph" : self.signature_uri},
        )
        return None
    
    @property
    def properties_uri(self):
        return "{}{}_model_properties".format(settings.OCHRE_NAMESPACE, self.id)

    def query_properties(self, query):
        resp = requests.post(
            os.path.join(settings.JENA_URL, "ochre", "query"),
            data=OQ(query),
            headers={
                "Content-Type" : "application/sparql-query",
                "Accept" : "application/sparql-results+xml",
                "charset" : "utf-8"
            },
            params={"default-graph-uri" : [self.properties_uri, settings.ONTOLOGY_URI]}
        )
        return Result.parse(
            source=io.StringIO(
                resp.content.decode("utf-8")
            )
        )
    
    @property
    def properties(self):
        resp = requests.get(
            "{}/ochre/data".format(settings.JENA_URL),
            params={"graph" : self.properties_uri},
            headers={"Accept" : "text/turtle", "charset" : "utf-8"}
        )
        g = Graph()
        g.parse(data=resp.content, format="turtle")
        return g

    def delete_properties(self):
        resp = requests.delete(
            "{}/ochre/data".format(settings.JENA_URL),
            params={"graph" : self.properties_uri},
        )

    def apply(
            self,
            data_graph=None,
            domain_graph=None
    ):
        response = requests.post(
            "{}/v2/models/{}/infer".format(
                settings.TORCHSERVE_INFERENCE_ADDRESS,
                self.id
            ),
            data={
                "data_graph" : data_graph.serialize(format="turtle"),
                "domain_graph" : domain_graph.serialize(format="turtle")
            }
        )
        g = Graph()
        g.parse(data=response.content, format="turtle")
        return g

    def delete_from_torchserve(self, **argd):
        try:
            resp = requests.delete(
                "{}/models/{}".format(
                    settings.TORCHSERVE_MANAGEMENT_ADDRESS,
                    self.id
                )
            )
            os.remove(os.path.join(settings.MODELS_ROOT, "{}_model.mar".format(self.id)))
        except:
            pass
    
    def delete(self, **argd):
        uris = [self.properties_uri, self.signature_uri]
        clear.delay(self.id, uris)
        return super(MachineLearningModel, self).delete(**argd)
    
    def save(self, **argd):
        create = not (self.id and True)
        retval = super(MachineLearningModel, self).save()
        if "signature_file" in argd:
            self.delete_signature()
            store = rdf_store(settings=settings)
            ds = rdflib.Dataset(store=store)
            g = ds.graph(self.signature_uri)
            g.parse(source=argd["signature_file"], format="turtle")
            store.commit()
        if "properties_file" in argd:
            if not create:                
                self.delete_properties()
            g = rdflib.Graph()
            g.parse(source=argd["properties_file"])
            every = 10000
            store = rdf_store(settings=settings, autocommit=False)
            ds = rdflib.Dataset(store=store)
            pg = ds.graph(self.properties_uri)
            for i, tr in enumerate(g):
                pg.add(tr)
                if i % every == 0:
                    store.commit()
            if i % every != 0:
                store.commit()
        if "mar_file" in argd:
            if not create:
                self.delete_from_torchserve()
            mname = os.path.join(
                settings.MODELS_ROOT,
                "{}_model.mar".format(self.id)
            )
            with open(mname, "wb") as ofd:
                ofd.write(argd["mar_file"].read())
            task = load_model.delay(
                self.id,
                os.path.basename(mname)
            )
        return retval


@shared_task
def load_model(obj_id, mar_url, *argv, **argd):
    obj = MachineLearningModel.objects.get(id=obj_id)
    obj.state = obj.PROCESSING
    resp = requests.post(
        "{}/models".format(settings.TORCHSERVE_MANAGEMENT_ADDRESS),
        params={
            "model_name" : obj.id,
            "url" : mar_url,
            "initial_workers" : 1,
        },
    )
    if resp.status_code == requests.codes.ok:
        obj.state = obj.COMPLETE
    else:
        obj.delete()
