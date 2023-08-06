import re
import json
import logging
import pickle
import gensim
import rdflib
import io
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, Namespace, XSD
from rdflib.query import Result
from ts.torch_handler.base_handler import BaseHandler
from pyochre.server.ochre import settings
from pyochre.utils.ochreturtle import ochreturtle as OT
from pyochre.utils.ochrequery import ochrequery as OQ
import requests


logger = logging.getLogger(__name__)


class OchreHandler(BaseHandler):

    def __init__(self, *argv, **argd):
        super(OchreHandler, self).__init__(*argv, **argd)

    def initialize(self, context):
        self.signature = Graph()
        self.signature.parse(
            data=OT(context.manifest["model"]["modelSignature"]),
            format="turtle"
        )
        self.properties = context.manifest["model"]["properties"]
        with open(
                context.manifest["model"]["serializedFile"],
                "rb"
        ) as ifd:
            _, self.model, _ = pickle.loads(ifd.read())

    def handle(self, data, context):
        retval = []
        for batch in data:
            qres = Result.parse(
                source=io.BytesIO(
                    batch["data"]
                ),
                format="xml"
            )
            g = self.handle_batch(qres)
            retval.append(
                {
                    "output_graph" : g.serialize(format="turtle")
                }
            )
        return retval
