import hashlib
import json
import io
from importlib.resources import files
from rdflib import Dataset, Namespace, URIRef, Graph
from rdflib.namespace import RDF, SH
from rdflib.query import Result
from rdflib.plugins.sparql import prepareQuery
from pyochre.server.ochre.settings import OCHRE_NAMESPACE


OCHRE = Namespace(OCHRE_NAMESPACE)

def create_domain(primarysource):
    domain_query = files("pyochre").joinpath("data/domain_query.sparql").read_text()
    entities = {}
    #for binding in Result.parse(
            #source=io.StringIO(
                #json.dumps(
    for binding in primarysource.query(
            domain_query
    ):
                    #connection.post(
                    #    primarysource["query_url"],
                    #    {"query" : domain_query}
                    #)
                #),
    #        ),
    #        format="xml"            
    #):
        vals = {}
        for vn in ["st", "p", "ot", "odt"]:
            vals[vn] = binding.get(vn)
        if not (vals["ot"] or vals["odt"]):
            continue
        entities[vals["st"]] = entities.get(
            vals["st"],
            {"name" : vals["st"], "properties" : {}}
        )
        entities[vals["st"]]["properties"][vals["p"]] = entities[vals["st"]]["properties"].get(
            vals["p"],
            {
                "name" : vals["p"],
                "type" : "data" if vals["odt"] else "class",
                "values" : set()
            }
        )
        if vals["odt"]:
            entities[vals["st"]]["properties"][vals["p"]]["values"].add(vals["odt"])
        else:
            entities[vals["st"]]["properties"][vals["p"]]["values"].add(vals["ot"])
            entities[vals["ot"]] = entities.get(
                vals["ot"],
                {"name" : vals["ot"], "properties" : {}}
            )
    #entities = {}
    g = Graph()
    for entity, edges in entities.items():
        if not entity:
            continue
        #print(entity)
        g.add((entity, RDF.type, SH.NodeShape))
        g.add((entity, SH.name, edges["name"]))        
        for pred, obj in edges["properties"].items():
            # fill in 
            h = hashlib.sha1()
            h.update(
               bytes(str((entity, pred, obj)), "utf-8")
            )
            uid = h.hexdigest()
            prop = OCHRE[uid]
            g.add((entity, SH.property, prop))
            g.add((prop, SH["path"], pred))
            g.add((prop, SH["nodeKind"], SH["IRI"]))
            g.add((prop, SH["name"], obj["name"]))
            obj["values"] = [v for v in obj["values"] if v != None]
            if len(obj["values"]) == 1:
                g.add((prop, SH["class"] if obj["type"] == "class" else SH["datatype"], list(obj["values"])[0]))
            else:
                uidd = OCHRE[uid + "_or"]
                g.add((prop, SH["or"], uidd))
                for i, v in enumerate(obj["values"]):
                    g.add((uidd, SH["class"], v))
    
    return g
