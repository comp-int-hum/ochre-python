from wikidata.client import Client
import re
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDFS

WDT = Namespace("http://www.wikidata.org/prop/direct/")

def enrich_uris(uris):
    wd_client = Client()
    retval = []
    for uri in uris:
        wid = re.match(r".*((?:P|Q)\d+)$", uri).group(1)
        wd_info = wd_client.get(wid)
        retval += [
           (uri, WDT["P2561"], Literal(wd_info.label)),
           (uri, RDFS["comment"], Literal(wd_info.description)),
        ]
    return retval
