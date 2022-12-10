import logging
import re
from uuid import uuid4
import functools
import os.path
import rdflib
from rdflib.term import BNode, URIRef, Literal
from pyochre.utils import meta_open
from jsonpath_ng import jsonpath, parse
from wikidata.client import Client


def as_list(item):
    return item if isinstance(item, list) else [item]


cached_paths = {}
def run_jsonpath(m, obj):
    path = m.group(1)
    if path == "":        
        return "{}_{}_bnode".format(obj["id"], obj["tag"])
    else:
        if path not in cached_paths:
            cached_paths[path] = parse(path)
        jp = cached_paths[path]
        vals = jp.find(obj)
        return str(vals[0].value)


logger = logging.getLogger("pyochre.primary_sources.processor")


def expand(schema):
    retval = {k : v for k, v in schema.items()}
    retval["rules"] = [
        {
            "match" : r["match"] if isinstance(r["match"], list) else [r["match"]],
            "create" : r["create"] if isinstance(r["create"], list) else [r["create"]]
        } for r in schema.get("rules", [])
    ]
    return retval


class Processor(object):
    output = True
    output_files = {}
    path = []
    buffers = {
        "domain" : [],
        "data" : [],
        "materials" : []
    }
    max_buffer_sizes = {
        "domain" : 50000,
        "data" : 50000,
        "materials" : 5000
    }
    wd_set = set()
    wd_client = Client()
    
    def __init__(
            self,
            name,
            schema,
            domain_file=None,
            data_file=None,
            materials_file=None,            
            connection=None,
            replace=False
    ):
        """
        A Processor takes a method that, given some inputs, generates a stream of
        items, each of which are either a *domain* triple, a *data* triple, or a
        *materials* triple, and streams them either to files or to an OCHRE server.
        """

        self.connection = connection
        self.name = name        
        self.schema = expand(schema if schema else {})
        self.domain_file = domain_file
        self.data_file = data_file
        self.materials_file = materials_file
        self.location = []
        self.replace = replace
        self.output = "connection"
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
            logger.warning("No output files were specified, and no valid connection is available, so there's nowhere to store results")
            self.output = False
    
    def __call__(self, fd):
        self.location = []
        max_events = 3000
        for rule in self.schema.get("predefined", []):
            #def create(self, creation_rule, event_type, tag, attributes, text, location, uid, index):
            self.create(
                rule,
                "",
                "",
                {},
                "",
                [],
                "",
                0
            )
        for i, (event_type, tag, attributes, text) in enumerate(self.generate_events(fd)):
            if max_events and i >= max_events:
                break
            
            if event_type == "start":
                uid = uuid4().hex
                if len(self.location) > 0:
                    self.location[0]["child_indices"][tag] = self.location[0]["child_indices"].get(tag, 0) + 1
                self.location = [
                    {
                        "event_type" : event_type,
                        "tag" : tag,
                        "attributes" : attributes,
                        "text" : text,
                        "id" : uid,
                        "child_indices" : {}
                        #"index" : 0 if len(self.location) == 0 else self.location[0]["child_indices"][tag]
                    }
                ] + self.location

            elif event_type == "end":
                
                for k, v in self.location[0]["attributes"].items():
                    attributes[k] = v
                self.location = self.location[1:]
                index = 0 if len(self.location) == 0 else self.location[0]["child_indices"].get(tag, 0)
                self.process_event(event_type, tag, attributes, text, self.location, uid, index)
            else:
                raise Exception("Unknown event type '{}'".format(event_type))
            

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Handle anything that remains in the buffers
        for buffer_name in list(self.buffers.keys()):
            if len(self.buffers[buffer_name]) > 0:
                self.store_buffer(buffer_name)
                
    def generate_events(self, fd): pass

    def matches(self, match_rule, event_type, tag, attributes, text, location):
        location_matches = True
        attributes_match = True
        tag_matches = True
        event_type_matches = event_type in as_list(match_rule.get("event_type", event_type))
        if event_type_matches:
            tag_matches = match_rule.get("tag", None) == None or tag in as_list(match_rule["tag"])
            if tag_matches:
                for k, v in match_rule.get("attributes", {}).items():
                    if attributes.get(k, None) not in as_list(v): # or (v != None and attributes.get(k, None) != v):
                        attributes_match = False
                        break                
                if attributes_match:
                    
                    location_matches = all(
                        [
                            self.matches(
                                lrule,
                                "start",
                                loc.get("tag", None),
                                loc.get("attr", {}),
                                text,
                                []
                            ) for lrule, loc in zip(reversed(match_rule.get("location", [])), location)
                        ]
                    )
        return event_type_matches and tag_matches and location_matches and attributes_match

    def expand(self, template, context):
        if not template:
            return template
        else:
            return re.sub(r"\{(.*?)\}", functools.partial(run_jsonpath, obj=context), template)
    
    def make_term(self, term_spec, event_type, tag, attributes, text, location, uid, index, triple_type):
        context = {
            "event_type" : event_type,
            "tag" : tag,
            "attributes" : attributes,
            "text" : text,
            "location" : location,
            "id" : uid,
            "index" : index
        }
        if term_spec["type"] == "uri":
            retval = URIRef(
                value=(self.schema.get("namespaces", {}).get(term_spec["namespace"]) if "namespace" in term_spec else "") + self.expand(term_spec["value"], context)
            )
            if term_spec.get("namespace", None) in ["wde", "wdp"]:
                wd = term_spec["value"]
                if wd not in self.wd_set:
                    self.wd_set.add(wd)
                    wd_info = self.wd_client.get(wd)
                    self.add(
                        triple_type,
                        {
                            "subject" : retval,
                            "predicate" : self.make_term(
                                {
                                    "value" : "P2561",
                                    "namespace" : "wdp",
                                    "type" : "uri"
                                },
                                event_type,
                                tag,
                                attributes,
                                text,
                                location,
                                uid,
                                index,
                                triple_type
                            ),
                            #"predicate" : URIRef("wdp:label"),
                            "object" : Literal(wd_info.label)
                        }
                    )
                    self.add(
                        triple_type,
                        {
                            "subject" : retval,
                            "predicate" : self.make_term(
                                {
                                    "value" : "comment",
                                    "namespace" : "rdfs",
                                    "type" : "uri"
                                },
                                event_type,
                                tag,
                                attributes,
                                text,
                                location,
                                uid,
                                index,
                                triple_type
                            ),
                            "object" : Literal(wd_info.description)
                        }
                    )
            return retval
        elif term_spec["type"] == "literal":
            dt = rdflib.namespace.XSD[term_spec.get("datatype")] if "datatype" in term_spec else None
            return Literal(
                lexical_or_value=self.expand(term_spec["value"], context),
                lang=term_spec.get("language", None), #self.expand(term_spec.get("language", None), context),
                datatype=dt, #self.expand(term_spec.get("datatype", None), context)
            )
        elif term_spec["type"] == "bnode":
            return BNode(
            )
        else:
            raise Exception("Unknown term type '{}'".format(term_spec["type"]))
    
    def make_triple(self, subj, pred, obj, event_type, tag, attributes, text, location, uuid, index, triple_type):
        return {
            "subject" : self.make_term(subj, event_type, tag, attributes, text, location, uuid, index, triple_type),
            "predicate" : self.make_term(pred, event_type, tag, attributes, text, location, uuid, index, triple_type),
            "object" : self.make_term(obj, event_type, tag, attributes, text, location, uuid, index, triple_type),
        }
    
    def create(self, creation_rule, event_type, tag, attributes, text, location, uid, index):
        subj = creation_rule["subject"]
        for pred_obj in creation_rule.get("predicate_objects", [{"predicate" : creation_rule.get("predicate"), "object" : creation_rule.get("object")}]):
            pred = pred_obj["predicate"]
            obj = pred_obj["object"]
            #subj = pred_obj[""]
            #subj_uri = self.make_term(subj, event_type, tag, attributes, text, location, uuid)
            self.add(
                creation_rule["type"],
                self.make_triple(subj, pred, obj, event_type, tag, attributes, text, location, uid, index, creation_rule["type"])
            )
    
    def process_event(self, event_type, tag, attributes, text, location, uid, index):
        logger.debug(
            "Saw event of type '%s', tag '%s', attributes '%s', text content of %d characters, and location %s",
            event_type,
            tag,
            attributes,
            len(text) if text else 0,
            location
        )
        for rule in self.schema["rules"]:            
            match_rules = as_list(rule["match"])
            creation_rules = as_list(rule["create"])
            if any([self.matches(match_rule, event_type, tag, attributes, text, location) for match_rule in match_rules]):
                for creation_rule in creation_rules:
                    self.create(creation_rule, event_type, tag, attributes, text, location, uid, index)
    
    def add(self, triple_type, triple):
        self.buffers[triple_type].append(triple)
        #self.location[-1][-1].append(triple)
        #self.location[0]["triples"].append(triple)
        if len(self.buffers[triple_type]) >= self.max_buffer_sizes[triple_type]:
            self.store_buffer(triple_type)

    # unicode char P487
    def store_buffer(self, buffer_name):
        #logger.info("Storing %d items from buffer %s", len(self.buffers[buffer_name]), buffer_name)
        graph = rdflib.Graph(bind_namespaces="none")
        for name, space in self.schema.get("namespaces", {}).items():
            graph.bind(name, rdflib.Namespace(space))
        for triple in self.buffers[buffer_name]:
            graph.add(
                (
                    triple["subject"],
                    triple["predicate"],
                    triple["object"]
                )
            )            
        if not self.output:
            logger.warning(
                "No way to store it, but would store %d %s triples, such as %s",
                len(self.buffers[buffer_name]),
                buffer_name,
                self.buffers[buffer_name][0]
            )
        elif self.output == "connection":
            existing = None
            for ps in self.connection.get_objects("primarysource")["results"]:
                if ps["name"] == self.name and ps["creator"] == self.connection.user:
                    existing = ps["url"]
            if not existing:
                raise Exception("Something went wrong: couldn't find primary source '{}' created by '{}'".format(self.name, self.connection.user))
            else:
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
        
