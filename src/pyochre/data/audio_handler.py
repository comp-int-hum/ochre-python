import logging
from ts.torch_handler.base_handler import BaseHandler
import pickle
import gensim
import rdflib
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, Namespace
from datasets import Audio
from pyochre.server.ochre import settings


logging.basicConfig(level=logging.INFO)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")


class Handler(BaseHandler):
    
    def initialize(self, context):
        with open(context.manifest["model"]["serializedFile"], "rb") as ifd:
            self.preprocessor, self.model, self.postprocessor = pickle.loads(ifd.read())

    def graph():
        pass

    def query():
        pass

    def generator():
        pass

    def singleton(self, ifd):

        pass
            
    def handle(self, data, context):
        retval = []        
        for batch in data:
            if batch.get("domain_graph"):
                pass
            else:
                retval.append(self.singleton(batch["file"]))
        return retval
