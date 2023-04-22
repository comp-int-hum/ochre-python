import logging
import json
import os.path
import os
from django.conf import settings
import requests
import rdflib
from pyochre.server.ochre.models import OchreModel, AsyncMixin
from pyochre.utils import rdf_store, to_graph, from_graph
from pyochre.server.ochre.decorators import ochre_cache_method
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, Namespace


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


logger = logging.getLogger(__name__)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


class MachineLearningModel(AsyncMixin, OchreModel):
    
    @property
    def signature(self, *argv, **argd):
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)
        g = rdflib.Graph()
        for tr in ds.triples((None, None, None, self.signature_uri)):
            g.add(tr)
        return g
    
    @property
    def signature_uri(self):
        return "{}{}_model_signature".format(settings.OCHRE_NAMESPACE, self.id)

    @property
    def signature(self):
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)
        g = rdflib.Graph()
        for tr in ds.triples((None, None, None, self.signature_uri)):
            g.add(tr)
        return g #.serialize(format="json-ld")
    
    @property
    def properties_uri(self):
        return "{}{}_model_properties".format(settings.OCHRE_NAMESPACE, self.id)

    def query_properties(self, query):
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
        return store.query(
            pquery,
            queryGraph=self.properties_uri
        )
    
    @property
    def properties(self):
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)
        g = rdflib.Graph()
        for tr in ds.triples((None, None, None, self.properties_uri)):
            g.add(tr)
        return g #.serialize(format="json-ld")

    
    def apply(
            self,
            #singleton=None,
            #query_results=None,
            data_graph=None,
            domain_graph=None
    ):
        
        #data = {}
        #print(123123)
        #return None
        #if singleton:
        #    data["singleton"] = json.dumps(singleton)
        #elif query_results:
        #    print(type(query_results), type(domain_graph))
        #    data["query_results"] =
        #data = query_results.serialize(format="xml")
        #print(data)
            #json.dumps(query_results)
        #    data["domain_graph"] = domain_graph.serialize("turtle")
        #else:
        #    data["data_graph"] = json.dumps(data_graph)
        #    data["domain_graph"] = domain_graph.serialize("turtle")#json.dumps(domain_graph)
        response = requests.post(
            "{}/v2/models/{}/infer".format(
                settings.TORCHSERVE_INFERENCE_ADDRESS,
                self.id
            ),
            data={
                "data_graph" : data_graph.serialize(format="turtle"),
                "domain_graph" : domain_graph.serialize(format="turtle")
            }
            #files={k : v[0] if isinstance(v, list) else v for k, v in argd.items()}
        )
        
        return response.content
    
    def delete_signature(self):
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)        
        ds.remove_graph(self.signature_uri)
        ds.commit()
        return None
    
    def delete_properties(self):
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)        
        ds.remove_graph(self.properties_uri)
        ds.commit()
        return None

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
        resp = requests.delete(
            "{}/models/{}".format(
                settings.TORCHSERVE_MANAGEMENT_ADDRESS,
                self.id
            )
        )
        model_file = os.path.join(settings.MODELS_ROOT, "{}_model.mar".format(self.id))
        if os.path.exists(model_file):
            os.remove(os.path.join(settings.MODELS_ROOT, "{}_model.mar".format(self.id)))
        self.delete_signature()
        self.delete_properties()        
        return super(MachineLearningModel, self).delete(**argd)
    
    def save(self, **argd):
        create = not (self.id and True)
        self.state = self.COMPLETE
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
                    print(i)
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
