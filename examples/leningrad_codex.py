
import os.path
import logging
import tarfile
from pyochre.utils import Command, Config, fetch_from_url
from pyochre.primary_sources import XmlProcessor


logger = logging.getLogger("pyochre.examples.leningrad_codex")


data_url = "http://www.logical-space.org/wlc_dh.tgz"
schema = {
    # directly-specified information
    "external" : {
        "P" : "Q514434",
        "J" : "Q1099313",
        "E" : "Q659765",
        "Dtr1" : "Q475346",
        "Dtr2" : "Q475346",
        "R" : "",
        "Other" : "",
    },
    
    # corresponds to the specific given entity
    "unique_entity_elements" : {
        "tanach" : "Q732870"
    },
    
    # corresponds to entity of the given type
    "structural_elements" : {
        "book" : "Q29154430",
        "c" : "Q29154515",
        "v" : "Q29154550",
        "w" : "Q82837422", # lexical token
        "m" : "Q2626534" # substring
    },

    # corresponds to a value for the given property on the current entity
    "property_elements" : {
        "name" : "P2561",
        "number" : "P1545",
    },

    # corresponds to a value for the given property on the entity associated with the current element
    "property_attributes" : {
        "n" : "P1545",
    },
    
    # corresponds to the given relationship holding between the entity associated with the
    # element being processed and the most-recent ancestor entity
    "relationship_elements" : {
        "book" : "P361",        
        "c" : "P361",
        "v" : "P361",
        "w" : "P361",
        "m" : "P361",        
    },

    # corresponds to the given relationship holding between the entity associated with the
    # element being processed and the URI derived from the attribute value
    "relationship_attributes" : {
        "s" : "P50"
    },

    "element_content" : {
        
    }
    #"content_passthrough_elements" : [],
    #"relationships" : {}
}


schema = {
    "metadata" : {},
    "predefined" : [],
    "namespaces" : {
        "cdh" : "https://cdh.jhu.edu/",
        "xsd" : "http://www.w3.org/2001/XMLSchema#",
        "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
        "shacl" : "http://www.w3.org/ns/shacl#",
        "sdo" : "https://schema.org/",
        "wde" : "https://www.wikidata.org/wiki/",
        "wdp" : "https://www.wikidata.org/wiki/Property:",
        "owl" : "http://www.w3.org/2002/07/owl#",
        "qb" : "http://purl.org/linked-data/cube#",
        "prov" : "http://www.w3.org/ns/prov#",
        "geo" : "http://www.opengis.net/ont/geosparql#"
    },
    "rules" : [
        {
            "match" : {
                "event_type" : "start",
                "tag" : "book",
            },
            "create" : {
                "type" : "data",
                "subject" : {
                    "type" : "uri",
                    "value" : "{}",
                    "namespace" : "cdh"
                },
                "predicate" : {
                    "type" : "uri",
                    "value" : "type",
                    "namespace" : "rdf"
                },
                "object" : {
                    "type" : "uri",
                    "value" : "Q29154430",
                    "namespace" : "wde"
                }
            }
        },
        {
            "match" : {
                "event_type" : "end",
                "tag" : "name",
                "location" : [
                    {"tag" : "names"},
                    {"tag" : "book"}
                ]
            },
            "create" : {
                "type" : "data",
                "subject" : {
                    "type" : "uri",
                    "value" : '{location[3][4][0][0]}',
                },
                "predicate" : {
                    "type" : "uri",
                    "value" : "label",
                    "namespace" : "rdfs"
                },
                "object" : {
                    "type" : "literal",
                    "value" : "{text}",
                    "xml:lang" : "en"
                }
            }
        }
    ]
}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

with Config(mode="r") as config:
    try:
        connection = Connection(config)
    except:
        logger.warning("Couldn't connect or authenticate with server, so REST actions not available")
        connection = False
    
    proc = XmlProcessor(
        "Leningrad Codex of the Hebrew Bible",
        schema,
        connection=connection
    )
    fname = fetch_from_url(data_url, config)
    with tarfile.open(fname, "r:gz") as tfd:
        for member in tfd.getmembers():
            if member.isfile() and member.name.endswith("xml"):
                x = proc(tfd.extractfile(member))

                #pass
                #for triple in process_tei(
                #        tfd.extractfile(member).read(),
                #        schema
                #):
                #    print(triple)

