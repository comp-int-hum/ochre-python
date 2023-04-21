import logging
import sys
import io
import os
import json
import tarfile
from pyochre.server.ochre import settings
from pyochre.utils import Command, meta_open
from pyochre.primary_sources import TsvParser, CsvParser, JsonParser, create_domain, enrich_uris, NoHeaderTsvParser, NoHeaderCsvParser, XmlParser
from lxml.etree import XML, XSLT, parse, TreeBuilder, tostring, XSLTExtension
import rdflib
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib import Dataset, Namespace, URIRef, Literal, BNode
from rdflib.graph import BatchAddGraph


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


logger = logging.getLogger("pyochre.primary_sources")


formats = {
    "csv" : CsvParser,
    "tsv" : TsvParser,
    "ncsv" : NoHeaderCsvParser,
    "ntsv" : NoHeaderTsvParser,    
    "xml" : XmlParser,
    "json" : JsonParser,
    #"jsonl" : JsonlParser,
}


def skolemize(node):
    if isinstance(node, BNode):
        return node.skolemize()

def delete_primary_source(args, connection):
    obj = connection.get_object("primarysource", args.name)
    connection.delete(obj["url"])


def list_primary_sources_and_queries(args, connection):
    print("Primary sources:")
    for primarysource in connection.get_objects("primarysource")["results"]:
        print("%d: %s" % (primarysource["id"], primarysource["name"]))
    print("Queries:")
    for query in connection.get_objects("query")["results"]:
        print("%d: %s" % (query["id"], query["name"]))


def create_query(args, connection):
    with open(args.query_file, "rt") as ifd:
        sparql = ifd.read()
    obj = connection.create_or_update_object(
       model_name="query",
       object_name=args.name,
       data={"name" : args.name, "sparql" : sparql}
    )

    
def perform_query(args, connection):
    primarysource = connection.get_object("primarysource", args.primary_source_name)
    if args.query_name:
        query = connection.get_object("query", args.query_name)
        results = connection.post(
            query["perform_url"],
            {"query" : query["id"], "primarysource" : primarysource["id"]},
            expected=200
        )
    else:
        with open(args.query_file, "rt") as ifd:
            query = ifd.read()
            results = connection.post(
                primarysource["query_url"],
                {"query" : query},
                expected=200
            )

    if args.output_file:
        with open(args.output_file, "wt") as ofd:
            ofd.write(json.dumps(results, indent=4))


def create_primary_source(args, connection):

    # load the XML-to-RDF transformation rules
    with meta_open(args.xslt_file, "rt") as ifd:
        transform = XSLT(parse(ifd))

    # instantiate the specified X-to-XML parser
    parser = formats[args.input_format]()

    # create XML from the primary sources
    with meta_open(args.input_file, "rt") as ifd:
        xml = parser(ifd)

    if args.output_xml_file:
        with open(args.output_xml_file, "wb") as ofd:
            xml.getroottree().write(ofd, pretty_print=True)

    # create RDF from the XML (lots of memory!)
    tr = transform(xml)

    
    # load the RDF and skolemize it
    g = rdflib.Graph(base="http://test/")
    g.parse(data=tostring(tr), format="xml", publicID=OCHRE)
    g = g.skolemize()

    if args.output_rdf_file:
        with open(args.output_rdf_file, "wt") as ofd:
            ofd.write(g.serialize(format="turtle"))

    # create or replace the primary source graph on the RDF server
    obj = connection.create_or_replace_object(
       model_name="primarysource",
       object_name=args.name,
       data={"name" : args.name}
    )

    # create dataset handle from a SPARQL connection to the RDF server
    store = SPARQLUpdateStore(
        query_endpoint=obj["query_url"],
        update_endpoint=obj["update_url"],
        autocommit=False,
        returnFormat="json",
    )
    dataset = Dataset(store=store, default_graph_base=OCHRE)

    #get the named graph corresponding to the primary source
    ng = dataset.graph(
        OCHRE["{}_data".format(obj["id"])]
    )

    # information to collect
    uris = set()
    potential_materials = {}
    ignore = set()
    materials = {}

    modalities = {
        OCHRE[x] : x for x in [
            "image",
            "video",
            "text",
            "audio",
            "tensor"
        ]
    }
    
    #for s, p, o in g:
    #    if p in modalities:
    #        potential_materials[o] = modalities[p]
            
    #for uri, name in modalities.items():
    #    ng.add((uri, OCHRE["hasLabel"], Literal(name)))
        
    #for s, _, o in g.triples((None, OCHRE["hasLabel"], None)):
    #    if s in potential_materials:
    #        fname = os.path.join(args.base_path, o)
    #        if os.path.exists(fname):
    #            materials[s] = (fname, potential_materials[s])
    #        else:
    #            ignore.add(s)
                
    for s, p, o in g:
        #if s in ignore or o in ignore:
        #    continue
        for n in [s, p, o]:
            if isinstance(n, URIRef) and "wikidata" in n:
                uris.add(n)
        ng.add(
            (
                s,
                p,
                o
            )
        )
    store.commit()
    ng = dataset.graph(
        OCHRE["{}_domain".format(obj["id"])]
    )
    for s, p, o in create_domain(connection, obj):
        ng.add((s, p, o))
    store.commit()

    for uri, (fname, mode) in materials.items():
        ext = os.path.splitext(fname)[-1][1:]
        with open(fname, "rb") as ifd:
            connection.create_object(
                "material",
                {
                    "uid" : str(uri),
                    "content_type" : "{}/{}".format(mode, ext)
                },
                files={"file" : ifd}
            )
    

class PrimarySourcesCommand(Command):
    
    def __init__(self):
        super(PrimarySourcesCommand, self).__init__(
            prog="python -m pyochre.primary_sources"
        )        
        list_parser = self.subparsers.add_parser(
            "list",
            help="Print information about primary sources and queries on the server"
        )
        list_parser.set_defaults(func=list_primary_sources_and_queries)

        create_query_parser = self.subparsers.add_parser(
            "create_query"
        )
        create_query_parser.set_defaults(func=create_query)        
        create_query_parser.add_argument(
            "--query_file",
            dest="query_file",
            required=True
        )
        create_query_parser.add_argument(
            "--name",
            dest="name",
            required=True
        )
        create_query_parser.add_argument(
            "--replace",
            dest="replace",
            action="store_true",
            default=False,
            help="If the query already exists, replace it"
        )

        perform_query_parser = self.subparsers.add_parser(
            "perform_query"
        )
        perform_query_parser.set_defaults(func=perform_query)
        perform_query_parser.add_argument(
            "--query_name",
            dest="query_name",
            required=False
        )
        perform_query_parser.add_argument(
            "--query_file",
            dest="query_file",
            required=False
        )
        perform_query_parser.add_argument(
            "--primary_source_name",
            dest="primary_source_name",
            required=True
        )
        perform_query_parser.add_argument(
            "--output_file",
            dest="output_file",
            required=False
        )
        
        create_parser = self.subparsers.add_parser(
            "create",
            help="Create a primary source"
        )
        create_parser.set_defaults(func=create_primary_source)
        create_parser.add_argument(
            "--output_xml_file",
            dest="output_xml_file",
            help="Output XML file"
        )
        create_parser.add_argument(
            "--output_rdf_file",
            dest="output_rdf_file",
            help="Output RDF file"
        )
        create_parser.add_argument(
            "--input_file",
            dest="input_file",
            help="Input file"
        )
        create_parser.add_argument(
            "--input_format",
            dest="input_format",
            help="Format of input file",
            choices=formats.keys()
        )
        create_parser.add_argument(
            "--name",
            dest="name",
            required=True,
            help="Primary source name"
        )
        create_parser.add_argument(
            "--xslt_file",
            dest="xslt_file",
            help="XSLT file describing how to process the data tree"
        )
        create_parser.add_argument(
            "--replace",
            dest="replace",
            action="store_true",
            default=False,
            help="If the primary source already exists, replace it"
        )
        create_parser.add_argument(
            "--upload_materials",
            dest="upload_materials",
            action="store_true",
            default=False,
            help="Upload materials (images, etc)"
        )
        create_parser.add_argument(
            "--enrich",
            dest="enrich",
            action="store_true",
            default=False,
            help="Try to augment any WikiData references"
        )
        create_parser.add_argument(
            "--base_path",
            dest="base_path",
            help="Base path from which file names should be resolved for materials",
            default=os.getcwd()
        )
        
        delete_parser = self.subparsers.add_parser(
            "delete",
            help="Delete a primary source from the server"            
        )
        delete_parser.set_defaults(func=delete_primary_source)
        delete_parser.add_argument("--name", dest="name", required=True)


if __name__ == "__main__":
    PrimarySourcesCommand().run()
