import logging
import base64
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, Namespace, XSD
from pyochre.server.ochre import settings


OCHRE = Namespace(settings.OCHRE_NAMESPACE)
#W#D = Namespace("http://www.wikidata.org/entity/")
#W#DT = Namespace("http://www.wikidata.org/prop/direct/")

logger = logging.getLogger(__name__)


def from_graph(data):
    retval = []
    # g = Graph()
    # g.parse(data=data, format="turtle")
    # retval = [
    #     {"index" : t[0].value, "token" : t[1].value, "label" : t[2].value if t[2] else False} for t in g.query(
    #         """
    #         PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    #         SELECT ?i ?t ?l WHERE
    #         {
    #           ?n wdt:P2561 ?t .
    #           ?n wdt:P1545 ?i .
    #           OPTIONAL {
    #             ?n wdt:P1269 ?l .
    #           }
    #         } ORDER BY ?i
    #         """
    #     )        
    # ]
    # if len(retval) == 0:
    #     datum = [
    #         t for t in g.query(                
    #             """
    #             PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    #             SELECT ?t WHERE
    #             {
    #             ?n ochre:outputTextProperty ?t .
    #             }
    #             """
    #         )
    #     ]
    #     retval = datum[0]        
    return retval


def to_graph(data):    
    g = Graph()
    # if isinstance(data, str):
    #     for i, token in enumerate(data.split(" ")):
    #         b = BNode()
    #         [
    #             g.add(tr) for tr in [                
    #                 (
    #                     b,
    #                     W#DT["P1545"],
    #                     Literal(i)
    #                 ),
    #                 (
    #                     b,
    #                     W#DT["P2561"],
    #                     Literal(token.strip())
    #                 ),
    #             ]
    #         ]
    # else:
    #     dd = data.read()
    #     b = BNode()
    #     [
    #         g.add(tr) for tr in [
    #             (
    #                 b,
    #                 W#DT["P51"],
    #                 Literal(base64.b64encode(dd), datatype=XSD.base64Binary)
    #             ),
    #         ]
    #     ]
        #print(dir(data))
    return g

