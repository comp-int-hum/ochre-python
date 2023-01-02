import time
import logging
import re
from uuid import uuid4
import functools
import hashlib
import os
import os.path
import rdflib
from rdflib import Dataset, Namespace
from rdflib.term import BNode, URIRef, Literal
from rdflib.namespace import RDF, SH
from rdflib.plugins.stores.sparqlstore import SPARQLConnector, SPARQLUpdateStore, SPARQLStore
from rdflib.plugins.stores.memory import Memory as MemoryStore
from jsonpath_ng import jsonpath, parse
from wikidata.client import Client
from pyochre.utils import meta_open, rdf_store

OCHRE = Namespace("urn:ochre:")

default_namespaces = {
    "xsd" : "http://www.w3.org/2001/XMLSchema#",
    "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
    "shacl" : "http://www.w3.org/ns/shacl#",
    "sdo" : "https://schema.org/",
    "wd" : "http://www.wikidata.org/entity/",
    "wdt" : "http://www.wikidata.org/prop/direct/",
    "owl" : "http://www.w3.org/2002/07/owl#",
    "qb" : "http://purl.org/linked-data/cube#",
    "prov" : "http://www.w3.org/ns/prov#",
    "geo" : "http://www.opengis.net/ont/geosparql#",
    "ochre" : "urn:ochre:"
}


default_property_aliases = {
    "instance_of" : "P31",
    "name" : "P2561",
    "part_of" : "P361",
    "ordinal" : "P1545",
    "author" : "P50",
    "url" : "P2699"
}


default_entity_aliases = {
}


def as_list(item):
    return item if isinstance(item, list) else [item]


cached_paths = {}
def run_jsonpath(m, obj):
    path = m.group(1)
    if path == "":
        return obj["id"]
    else:
        if path not in cached_paths:
            cached_paths[path] = parse(path)
        jp = cached_paths[path]
        vals = jp.find(obj)
        return str(vals[0].value)


logger = logging.getLogger("pyochre.primary_sources.processor")


def expand_schema(schema):
    retval = [
        {
            "match" : as_list(
                r["match"] if isinstance(r["match"], list) else [r["match"]]
            ),
            "create" : as_list(
                r["create"] if isinstance(r["create"], list) else [r["create"]]
            ),
            "debug" : r.get("debug", False)
        } for r in schema.get("rules", []) if not r.get("skip", False)
    ]    
    return [(r["match"], r["create"], r["debug"]) for r in retval]


class Processor(object):
    output = True
    pending = 0
    output_files = {}
    path = []
    stack = [
        {
            "child_indices" : {}
        }
    ]
    buffers = {
        "domain" : [],
        "data" : [],
        "materials" : []
    }
    max_buffer_sizes = {
        "domain" : 50000,
        "data" : 50000,
        "materials" : 500
    }
    wd_lookup = {}
    observed_relationships = set()
    wd_client = Client()    
    materials = {}
    def expand_uri(self, template, context=None):
        tag = self.stack[-1]["tag"]
        if not context:
            context = {
                "tag" : self.stack[-1]["tag"],
                "attributes" : self.stack[-1]["attributes"],
                "text" : self.stack[-1]["text"],
                "location" : list(reversed(self.stack[:-1])),
                "id" : self.stack[-1]["uid"],
                "index" : self.stack[-2]["child_indices"].get(tag, 0)
            }
        if not template:
            return template
        else:
            return re.sub(r"\{(.*?)\}", functools.partial(run_jsonpath, obj=context), template)

    def __init__(
            self,
            name,
            schema,
            domain_file=None,
            data_file=None,
            materials_file=None,            
            connection=None,
            replace=False,
            enrich=False,
            base_path=None,
            upload_materials=False
    ):
        """
        A Processor takes a method that, given some inputs, generates a stream
        of items, each of which are either a *domain* triple, a *data* triple,
        or a *materials* triple, and streams them either to files or to an OCHRE
        server.
        """
        self.upload_materials = upload_materials
        self.name = name        
        self.connection = connection
        if self.connection:
            for ps in self.connection.get_objects("primarysource")["results"]:
                if ps["name"] == self.name and ps["creator"] == self.connection.user:
                    existing = ps
            self.store = SPARQLUpdateStore(
               query_endpoint=existing["sparql_query_url"],
               update_endpoint=existing["sparql_update_url"],
               autocommit=False,
               returnFormat="json",
            )
            self.id = existing["id"]
        else:
            self.store = MemoryStore()
        self.dataset = Dataset(store=self.store)
        #self.domain_graph = self.dataset.graph("domain")
        self.enrich = enrich
        self.connection = connection

        self.rules = expand_schema(schema if schema else [])
        self.schema = schema
        self.base_path = base_path if base_path else self.schema.get(
            "metadata",
            {}
        )
        self.namespaces = self.schema.get("namespaces", default_namespaces)
        self.base_namespace = self.schema.get("metadata", {}).get(
            "base_namespace",
            "urn:ochre:"
            #(self.connection.hostname if self.connection else "https://github.com/comp-int-hum/ochre-python/")
        )
        self.domain_file = domain_file
        self.data_file = data_file
        self.materials_file = materials_file
        self.replace = replace
        self.output = "connection"
        self.property_aliases = (
            default_property_aliases | self.schema.get("metadata", {}).get("aliases", {}).get("properties", {})
        )
        self.entity_aliases = (
            default_entity_aliases | self.schema.get("metadata", {}).get("aliases", {}).get("entities", {})
        )
        gen_types = set(sum([[c.get("type", None) for c in r["create"]] for r in self.schema["rules"]], []))
        if self.domain_file or self.data_file or self.materials_file:
            self.output = "files"
            for oname in ["domain", "data", "materials"]:
                fname = getattr(self, "{}_file".format(oname), None)
                if fname and oname in gen_types:
                    if os.path.exists(fname) and not self.replace:
                        self.output_files[oname] = meta_open(fname, "at")
                    else:
                        self.output_files[oname] = meta_open(fname, "wt")
        elif not self.connection:
            logger.warning(
                """
                No output files were specified, and no valid connection
                is available, so there's nowhere to store results
                """
            )
            self.output = False
    
    def __call__(self, fd):
        for i, (event_type, tag, attributes, text) in enumerate(
                self.generate_events(fd)
        ):
            if event_type == "start":
                # increment count of this tag relative to its parent location
                self.stack[-1]["child_indices"][tag] = self.stack[-1]["child_indices"].get(tag, 0) + 1
                # generate a unique ID for this location
                h = hashlib.sha1()
                h.update(
                    bytes(
                        str(
                            (event_type, tag, attributes, text, self.stack)
                        ),
                        "utf-8"
                    )
                )
                uid = h.hexdigest()
                # place the current location onto the stack
                self.stack.append(
                    {
                        "tag" : tag,
                        "attributes" : attributes,
                        "text" : text.strip() if text else "",
                        "uid" : uid,
                        "child_indices" : {}
                    }
                )
            elif event_type == "end":
                self.process_event()
                self.stack.pop()
            else:
                raise Exception("Unknown event type '{}'".format(event_type))
            
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pending > 0:
            logger.info("Adding %d triples to the data graph", self.pending)
            self.store.commit()
            self.pending = 0
        self.create_domain()
        self.run_upload_materials()
        
    def generate_events(self, fd): pass

    def matches(self, match_rule, info=None):
        if not info:
            info = self.stack[-1]
        tag_matches = match_rule.get("tag", None) == None or info["tag"] in as_list(match_rule["tag"])
        if tag_matches:
            for k, v in match_rule.get("attributes", {}).items():
                if info["attributes"].get(k, None) not in as_list(v):
                    return False
            location_matches = all(
                [
                    self.matches(
                        pred_rule,
                        pred_info
                    ) for pred_rule, pred_info in zip(reversed(match_rule.get("location", [])), list(reversed(self.stack))[1:])
                ]
            )
            if location_matches:
                return True
        return False
  
    def make_term(self, term_spec):
        tag = self.stack[-1]["tag"]
        context = {
            "tag" : self.stack[-1]["tag"],
            "attributes" : self.stack[-1]["attributes"],
            "text" : self.stack[-1]["text"],
            "location" : list(reversed(self.stack[:-1])),
            "id" : self.stack[-1]["uid"],
            "index" : self.stack[-2]["child_indices"].get(tag, 0)
        }
        # references to predefined WikiData entries
        if isinstance(term_spec, str):            
            if term_spec in self.property_aliases:
                term_spec = {"type" : "uri", "value" : self.property_aliases[term_spec], "namespace" : "wdt"}
            elif term_spec in self.entity_aliases:
                term_spec = {"type" : "uri", "value" : self.entity_aliases[term_spec], "namespace" : "wd"}
            else:
                raise Exception(
                    "Unknown WikiData entry alias '{}'".format(term_spec)
                )
        if term_spec["type"] == "uri":
            retval = URIRef(
                value=(
                    self.namespaces.get(term_spec["namespace"])
                    if "namespace" in term_spec
                    else self.base_namespace) + self.expand_uri(
                            term_spec["value"],
                            context
                    )
            )
            if term_spec.get("namespace", None) in ["wd", "wdt"] and self.enrich:
                self.enrich_term(term_spec, retval)
            return retval
        elif term_spec["type"] == "literal":
            dt = (
                rdflib.namespace.XSD[term_spec.get("datatype")]
                if "datatype" in term_spec
                else None
            )
            return Literal(
                lexical_or_value=self.expand_uri(term_spec["value"], context),
                lang=term_spec.get("language", None),
                datatype=dt,
            )
        elif term_spec["type"] == "bnode":
            return BNode()
        else:
            raise Exception("Unknown term type '{}'".format(term_spec["type"]))
    
    def make_triple(self, subj, pred, obj):
        return {
            "subject" : self.make_term(subj),
            "predicate" : self.make_term(pred),
            "object" : self.make_term(obj),
        }
    
    def create(self, creation_rule):
        subj = creation_rule["subject"]
        for pred_obj in creation_rule.get(
                "predicate_objects",
                [
                    {
                        "predicate" : creation_rule.get("predicate"),
                        "object" : creation_rule.get("object")
                    }
                ]
        ):
            
            pred = pred_obj["predicate"]
            obj = pred_obj["object"]
            triple = self.make_triple(subj, pred, obj)
            self.add(triple)
            if "file" in pred_obj:
                fname = os.path.join(
                    self.base_path,
                    self.expand_uri(pred_obj["file"])
                )
                if os.path.exists(fname):
                    with open(fname, "rb") as ifd:
                        data = ifd.read()
                        h = hashlib.sha1()
                        h.update(
                            data
                        )
                        uid = h.hexdigest()

                    tp = pred_obj["object_type"]
                    self.add(self.make_triple(obj, "instance_of", tp))
                    base = self.connection.base_url if self.connection else ""
                    self.add(
                        self.make_triple(
                            obj,
                            "url",
                            {
                                "type" : "uri",
                                "value" : "{}materials/{}/".format(
                                    base,
                                    uid
                                )
                            }
                        )
                    )
                    if self.upload_materials:
                        self.materials[uid] = (pred_obj["file_type"], fname)
                    
    def process_event(self):
        logger.debug(
            "Processing stack state %s",
            self.stack,
        )
        for match_rules, creation_rules, debug in self.rules:

            if any([self.matches(match_rule) for match_rule in match_rules]):
                for creation_rule in creation_rules:
                    self.create(creation_rule)

    def add(self, triple, triple_type="data"):
        self.pending += 1
        if any([x == None for x in triple.values()]):
            raise Exception(str(triple))
        self.dataset.add((triple["subject"], triple["predicate"], triple["object"], "{}{}_{}".format(self.base_namespace, self.id, triple_type)))
        if self.pending >= 50000:
            logger.info("Adding %d triples", self.pending)
            self.store.commit()
            self.pending = 0
            
    # unicode char P487
    def store_buffer(self, buffer_name):
        logger.info("Storing %d items from buffer %s", len(self.buffers[buffer_name]), buffer_name)
        graph = rdflib.Graph(bind_namespaces="none")
        graph.bind("ochre", self.base_namespace)
        for name, space in self.namespaces.items():
            graph.bind(name, rdflib.Namespace(space))
        for triple in self.buffers[buffer_name]:
            graph.add(
                (
                    triple["subject"],
                    triple["predicate"],
                    triple["object"]
                )
            )
        #if buffer_name == "data":
        if not self.output:
            logger.warning(
                "No way to store it, but would store %d %s triples, such as %s",
                len(self.buffers[buffer_name]),
                buffer_name,
                self.buffers[buffer_name][0]
            )
        elif self.output == "connection":
            pass
        elif self.output == "files":
            if buffer_name in self.output_files:
                logger.info(
                    "Storing %d triples in %s graph",
                    len(graph),
                    buffer_name
                )
                self.output_files[buffer_name].write(graph.serialize(format="turtle"))

        self.buffers[buffer_name] = []
        

    def enrich_term(self, term_spec, uri):
        wd = term_spec["value"]
        if wd not in self.wd_lookup:
            self.wd_lookup[wd] = self.wd_client.get(wd)
            wd_info = self.wd_lookup[wd]
            self.add(
                {
                    "subject" : uri,
                    "predicate" : self.make_term(
                        {
                            "value" : "P2561",
                            "namespace" : "wdt",
                            "type" : "uri"
                        }
                    ),
                    "object" : Literal(wd_info.label)
                }
            )
            self.add(
                {
                    "subject" : uri,
                    "predicate" : self.make_term(
                        {
                            "value" : "comment",
                            "namespace" : "rdfs",
                            "type" : "uri"
                        },
                    ),
                    "object" : Literal(wd_info.description)
                }
            )
            
    def create_domain(self):
        query = """
PREFIX ochre: <urn:ochre:>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT DISTINCT ?st ?stn ?p ?pn ?ot ?otn ?odtn
FROM ochre:%s_data
        WHERE
{
  
  {
    SELECT DISTINCT ?st ?stn ?p ?pn ?o WHERE
    {    
      # only care about subject entity-types with names
      ?st wdt:P2561 ?stn .
    
      # find instances of entities connected to an entity-type with a name
      ?s wdt:P31|(wdt:P460/wdt:P31) ?st .
    
      # only care about properties/relationships with names
      ?p wdt:P2561 ?pn .
    
      ?s ?p ?o .        
    
      # only care about entities defined directly in the OCHRE source
      filter (
        (strstarts(str(?s), str(ochre:))) &&
        (strstarts(str(?o), str(ochre:)) || (isLiteral(?o)))
      )
    }
  }

  OPTIONAL {
    ?o wdt:P31|(wdt:P460/wdt:P31) ?ot .
    ?ot wdt:P2561 ?otn .
  }

  BIND(IF(ISLITERAL(?o), DATATYPE(?o), "") as ?odtn)

}
""" % (self.id)
        entities = {}
        for r in self.dataset.query(query): #retval["results"]["bindings"]:
            st = r.get("st", None)
            stn = r.get("stn", None)
            p = r.get("p", None)
            pn = r.get("pn", None)
            ot = r.get("ot", None)
            otn = r.get("otn", None)
            odtn = r.get("odtn", None)
            entities[st] = entities.get(
                st,
                {"name" : stn, "properties" : {}}
            )
            entities[st]["properties"][p] = entities[st]["properties"].get(
                p,
                {
                    "name" : pn,
                    "type" : "data" if odtn else "class",
                    "values" : set()
                }
            )
            if odtn:
                entities[st]["properties"][p]["values"].add(odtn)
            else:
                entities[st]["properties"][p]["values"].add(ot)
                entities[ot] = entities.get(
                    ot,
                    {"name" : otn, "properties" : {}}
                )
        for entity, edges in entities.items():
            if not entity:
                continue
            self.add(                    
                {
                    "subject" : entity,
                    "predicate" : RDF.type,
                    "object" : SH.NodeShape
                },
                triple_type="domain"
            )
            self.add(                    
                {
                    "subject" : entity,
                    "predicate" : SH.name,
                    "object" : Literal(edges["name"])
                },
                triple_type="domain"
            )
            for pred, obj in edges["properties"].items():
                # fill in 
                h = hashlib.sha1()
                h.update(
                   bytes(str((entity, pred, obj)), "utf-8")
                )
                uid = h.hexdigest()
                prop = OCHRE[uid]
                # datatype, path
                self.add(
                    {
                        "subject" : entity,
                        "predicate" : SH.property,
                        "object" : prop
                    },
                    triple_type="domain"
                )
                self.add(
                    {
                        "subject" : prop,
                        "predicate" : SH["path"],
                        "object" : pred
                    },
                    triple_type="domain"
                )
                self.add(
                    {
                        "subject" : prop,
                        "predicate" : SH["nodeKind"],
                        "object" : SH["IRI"]
                    },
                    triple_type="domain"
                )
                self.add(
                    {
                        "subject" : prop,
                        "predicate" : SH["name"],
                        "object" : obj["name"]
                    },
                    triple_type="domain"
                )
                obj["values"] = [v for v in obj["values"] if v != None]
                if len(obj["values"]) == 1:
                    self.add(
                        {
                            "subject" : prop,
                            "predicate" : SH["class"] if obj["type"] == "class" else SH["datatype"],
                            "object" : list(obj["values"])[0]
                        },
                        triple_type="domain"
                    )
                else:
                    uidd = OCHRE[uid + "_or"]
                    self.add(
                        {
                            "subject" : prop,
                            "predicate" : SH["or"],
                            "object" : uidd
                        },
                        triple_type="domain"
                    )
                    for i, v in enumerate(obj["values"]):
                        self.add(
                            {
                                "subject" : uidd,
                                "predicate" : SH["class"],
                                "object" : v
                            },
                            triple_type="domain"
                        )
        if self.pending > 0:
            logger.info("Adding %d triples to the domain graph", self.pending)
            self.dataset.commit()
            
    def run_upload_materials(self):
        logger.info("Adding %d files", len(self.materials))
        for uid, (file_type, file_name) in self.materials.items():
            with open(file_name, "rb") as ifd:
                self.connection.post(
                    self.connection.endpoints["material"],
                    {"content_type" : file_type, "uid" : uid},
                    files={"file" : ifd}
                )

