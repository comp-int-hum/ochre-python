import json
import argparse
import re
import os.path
import os
import logging
from getpass import getpass
import requests
from pyochre.rest import Connection
from pyochre import env
from pyochre.utils import Command, meta_open
from pyochre.primary_sources import TsvParser, CsvParser, JsonParser, create_domain, enrich_uris, NoHeaderTsvParser, NoHeaderCsvParser, XmlParser, JsonLineParser
from lxml.etree import XML, XSLT, parse, TreeBuilder, tostring, XSLTExtension
import rdflib
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib import Dataset, Namespace, URIRef, Literal, BNode
from rdflib.graph import BatchAddGraph


logger = logging.getLogger("pyochre")


formats = {
    "csv" : CsvParser,
    "tsv" : TsvParser,
    "ncsv" : NoHeaderCsvParser,
    "ntsv" : NoHeaderTsvParser,    
    "xml" : XmlParser,
    "json" : JsonParser,
    "jsonl" : JsonLineParser,
}


def apply_transformation(connection, args):
    # load the XML-to-RDF transformation rules
    with meta_open(args["xslt_file"], "rt") as ifd:
        transform = XSLT(parse(ifd))

    # instantiate the specified X-to-XML parser
    parser = formats[args["input_format"]]()

    # create XML from the primary sources
    with meta_open(args["input_file"], "rt") as ifd:
        xml = parser(ifd).__next__()

        if args["output_xml_file"]:
            with open(args["output_xml_file"], "wb") as ofd:
                xml.getroottree().write(ofd, pretty_print=True, encoding="utf-8")

    # create RDF from the XML (lots of memory!)
    tr = transform(xml)
    
    # load the RDF and skolemize it
    g = rdflib.Graph(base="http://test/")
    g.parse(data=tostring(tr), format="xml", publicID=env("OCHRE_NAMESPACE"))
    g = g.skolemize()

    with open(args["output_rdf_file"], "wt") as ofd:
        ofd.write(g.serialize(format="turtle"))


def populate_materials(connection, args):
    list_url = re.sub(r"(\d+)\/?$", r"list_missing_materials/\1/", args["primarysource"])
    add_url = re.sub(r"(\d+)\/?$", r"add_missing_materials/\1/", args["primarysource"])
    finalize_url = re.sub(r"(\d+)\/?$", r"finalize_materials/\1/", args["primarysource"])
    mids = {}
    for fobj, fname in connection.action("get", list_url).json()["missing_file_names"].items():
        full_path = os.path.join(args["path"], fname)
        if os.path.exists(full_path):
            logger.info("Uploading '%s'", fname)            
            with open(full_path, "rb") as ifd:
                resp = connection.action("put", add_url, data={"name" : fname}, files={"file" : ifd})
                mids[fname] = resp.json()["material_id"]
        else:
            logger.info("No candidate file for '%s'", fname)
    if args.get("finalize", False):
        connection.action("post", finalize_url, data=mids)


def regenerate_ontology(connection, args):
    resp = connection.action("delete", args["url"])


def get_matches(connection, object_type, selector):
    for res in connection.action("get", connection.list_urls[object_type]).json():
        if all([res[k] == v for k, v in selector.items()]):
            yield res["url"]
            
def get_match(connection, object_type, payload):
    matches = []
    for res in connection.action("get", connection.list_urls[object_type]).json():        
        if object_type == "User" and payload["username"] == res["username"]:
            matches.append(res)
        elif object_type != "User" and payload["name"] == res["name"]:
            matches.append(res)
    if len(matches) == 0:
        raise Exception("Tried to update non-existent object")
    elif len(matches) > 1:
        raise Exception("Tried to update an object, but more than one object matches")
    else:
        return matches[0]
    
def batch_perform(connection, args):
    if args["full_reset"]:        
        for model_name in connection.list_urls.keys():
            if model_name != "Ontology":
                print(model_name)
                for item in connection.get_objects(model_name):
                    if not (model_name == "User" and item["username"] == connection.user):                        
                        connection.delete(item["url"])

    ops = {}
    for path, methods in connection.openapi["paths"].items():
        for method, props in methods.items():
            props["method"] = method
            props["path"] = "{}://{}:{}{}".format(env("PROTOCOL"), env("HOSTNAME"), env("PORT"), path)
            ops[props["operationId"]] = props
    for fname in args["inputs"]:
        with open(fname, "rt") as ifd:
            text = "\n".join([l for l in ifd if not re.match(r"^\s*\#.*", l)])
            for operation in json.loads(text):
                op = ops[operation["operationId"]]
                for item in operation["items"]:
                    payload = {k : v for k, v in operation.get("defaults", {}).items()}
                    files = {}
                    for k, v in item.items():
                        if isinstance(v, dict) and "path" in v:
                            files[k] = v["path"]
                        elif isinstance(v, dict) and "type" in v and "selectors" in v:
                            matches = []
                            for s in v["selectors"]:
                                matches += get_matches(connection, v["type"], s)
                            payload[k] = matches
                        else:                            
                            payload[k] = v
                    if op["method"].lower() in ["patch", "delete"]:
                        tp = os.path.basename(op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"])
                        m = get_match(connection, tp, payload)
                        path = op["path"].replace("{id}", str(m["id"]))
                        payload = {k : v for k, v in payload.items() if v}
                    else:
                        path = op["path"]
                    #print(op)
                            
                    resp = connection.action(op["method"], path, payload, files=files)
                    try:
                        print(json.dumps({k : v for k, v in resp.json().items() if v != None}, indent=4))
                    except:
                        print(resp.status_code)


class Command(object):
    connection = None
    
    def __init__(self, prog=None):
        env.read_env(env("ENVIRONMENT"))
        self.parser = argparse.ArgumentParser(
            prog="python -m pyochre",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
    def run(self):
        logging.basicConfig(level=getattr(logging, env("LOG_LEVEL")))
        connection = Connection()
        self.subparsers = self.parser.add_subparsers()
        #mp = self.subparsers.add_parser("Material")
        #mp.set_defaults(
        #    object_type="PrimarySource"
        #)
        #print(connection.openapi)
        #mps = mp.add_subparsers()
        op = self.subparsers.add_parser("Other")
        ops = op.add_subparsers()
        self.object_fields = {}
        self.namespace = connection.openapi["info"]["namespace"]
        list_urls = {}
        all_actions = {}
        for obj in connection.openapi["components"]["schemas"].keys():
            if obj in ["ContentType", "Documentation"]:
                continue
            actions = []
            for path, methods in connection.openapi["paths"].items():
                path = "{}://{}:{}{}".format(env("PROTOCOL"), env("HOSTNAME"), env("PORT"), path)
                relevant = False
                for method, method_info in methods.items():
                    tags = method_info["tags"]
                    if obj.lower() in tags:
                        relevant = True
                        if method_info["operationId"].startswith("list") and not method_info["operationId"].startswith("list_"):
                            list_urls[obj] = path

                if relevant:
                    actions.append((path, methods))
            
            if len(actions) > 0:
                sp = self.subparsers.add_parser(obj)
                sp.set_defaults(
                    object_type=obj,
                )
                ssps = sp.add_subparsers()
                for path, methods in actions:
                    for method_name, method in methods.items():
                        mid = method["operationId"]
                        action_name = re.sub(method["tags"][0] + "s?$", "", mid)
                        if mid not in all_actions:
                            all_actions[mid] = ssps.add_parser(
                                action_name,
                                help=method["description"],
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter
                            )
                        ssp = all_actions[mid]
                        ssp.set_defaults(
                            url=path,
                            method=method_name,
                            action_name=action_name
                        )
                        rb = method.get(
                            "requestBody", {}
                        ).get(
                            "content",
                            {}
                        ).get(
                            "application/json",
                            {}
                        ).get(
                            "schema",
                            {}
                        ).get(
                            "$ref",
                            ""
                        )                        
                        if rb:
                            schema_name = os.path.split(rb)[-1]
                            schema = connection.openapi["components"]["schemas"][schema_name]
                            for prop_name, prop in schema["properties"].items():
                                if not prop.get("readOnly", False):
                                    tp = prop.get("type", None)
                                    fm = prop.get("format", None)
                                    argp = {} if tp == "boolean" else {
                                        "type" : argparse.FileType("rb") if fm == "binary" else int if tp == "integer" else float if tp == "float" else str,
                                        "nargs" : "*" if tp == "array" else None,
                                    }
                                    #if (tp == "array" and prop["items"].get("format") == "object"):
                                    #    self.object_fields[(action_name, prop_name)] = prop["items"]["discriminator"]
                                    #elif prop.get("format") == "object" and "discriminator" in prop:
                                    #    self.object_fields[(action_name, prop_name)] = prop["discriminator"]            
                                    if prop.get("enum"):
                                        argp["choices"] = prop["enum"]
                                        
                                    ssp.add_argument(
                                        "--{}".format(prop_name),
                                        dest=prop_name,
                                        required=not prop.get("nullable", False),
                                        help=prop.get("description", None),
                                        default=prop.get("default", None),
                                        
                                        action="store_true" if tp == "boolean" else None,
                                        **argp
                                    )
                                    
                        for param in method["parameters"]:
                            tp = param["schema"]["type"]
                            if param["name"] == "id":
                                try:
                                    ssp.add_argument(
                                        "--object_name",
                                        dest="object_name",
                                        required=True,
                                        help="Name of object."
                                    )
                                    ssp.add_argument(
                                        "--object_creator",
                                        dest="object_creator",
                                        required=False,
                                        help="Username of object's creator.",
                                        default=env("USER")
                                    )
                                except:
                                    pass
                            else:
                                ssp.add_argument(
                                    "--{}".format(param["name"]),
                                    dest=param["name"],
                                    required=param.get("required", False),
                                    help=param["description"]
                                )

        batch = ops.add_parser(
            "batchPerform",
            description="Perform actions described in provided JSON file(s)."
        )
        batch.add_argument("--full_reset", dest="full_reset", action="store_true", help="Delete *all* existing information in the database before performing actions")
        batch.set_defaults(
            action_name="batchPerform",
            callback=batch_perform
        )
        batch.add_argument(dest="inputs", nargs="*", help="JSON file(s) describing the object to create.")
                                
        regenerate = ops.add_parser(
            "regenerateOntology",
            description="Regenerate the OCHRE ontology based on current settings and the state of the ochre.ttl file."
        )
        regenerate.set_defaults(
            action_name="regenerateOntology",
            callback=regenerate_ontology,
            url="{}://{}:{}/ontology/".format(
                env("PROTOCOL"),
                env("HOSTNAME"),
                env("PORT")
            )
        )
                                
        populate = ops.add_parser(
            "populateMaterials",
            description="Attempt to upload the specified primary source's materials (non-RDF files) from the contents of the specified directory.  This relies on the labels of the RDF file references being the same string as the files in the directory.  The 'finalize' option should only be specified if no more materials will be uploaded."
        )
        populate.set_defaults(
            action_name="populateMaterials",
            callback=populate_materials
        )
        populate.add_argument("--path", dest="path", help="Location of files to upload as materials.", required=True)
        populate.add_argument("--primarysource", dest="primarysource", help="Primary source to populate.", required=True)
        populate.add_argument("--finalize", dest="finalize", default=False, action="store_true", help="After uploading all available materials, finalize the primary source by removing all unsatisfied material references.")
        self.object_fields[("populateMaterials", "primarysource")] = "PrimarySource"
        
        transform = ops.add_parser(
            "applyTransformation",
            description="Transform the specified data file into XML and apply the specified style sheet to generate RDF, writing out both the intermediary XML and final RDF for inspection.  This allows for direct inspection of the process when writing a new transformation."
        )
        transform.set_defaults(
            action="applyTransformation",
            callback=apply_transformation
        )
        transform.add_argument(
            "--input_file",
            dest="input_file",
            help="Input file",
            required=True
        )
        transform.add_argument(
            "--input_format",
            dest="input_format",
            help="Format of input file",
            choices=formats.keys(),
            required=True
        )
        transform.add_argument(
            "--xslt_file",
            dest="xslt_file",
            help="XSLT file describing how to process the data tree",
            required=True
        )
        transform.add_argument(
            "--output_xml_file",
            dest="output_xml_file",
            help="Output XML file",
            required=True
        )
        transform.add_argument(
            "--output_rdf_file",
            dest="output_rdf_file",
            help="Output RDF file",
            required=True
        )
        
        
        args = self.parser.parse_args()
        vargs = vars(args)
        
        for k in list(vargs.keys()):
            key = (vargs.get("action_name"), k)
            if key in self.object_fields:
                success = False
                model = self.object_fields[key]                
                #if model == "ContentType":
                #    continue
                if not vargs[k]:
                    continue
                toks = vargs[k].split(":")
                if len(toks) == 2:
                    name, user = toks
                else:
                    name = toks[0]
                    user = env("USER")
                user_url = connection.user_urls.get(user, None)
                resp = connection.action("get", list_urls[model])
                for x in resp.json():

                    if x.get("creator_url") == user_url and x["name"] == name:
                        vargs[k] = x["url"]
                        success = True
                if not success:
                    raise Exception("Could not find {} matching name {} and creator {}".format(model, name, user))

        
        if "object_name" in vargs:
            obj = None
            for res in connection.action("get", list_urls[vargs["object_type"]]).json():
                if res["name"] == vargs["object_name"] and res["creator_url"] == connection.user_urls.get(vargs["object_creator"], None):
                    obj = res
            if not obj:
                raise Exception(
                    "Could not find {} with name {} and creator {}".format(
                        vargs["object_type"],
                        vargs["object_name"],
                        vargs["object_creator"],
                    )
                )
            vargs["url"] = obj["url"]

        if "callback" in vargs:
            vargs["callback"](connection, vargs)
        else:
            url = args.url.format(**vargs)

            data = {k : v for k, v in vargs.items() if isinstance(v, (int, str, float, list, bool))}
            files = {k : v for k, v in vargs.items() if not isinstance(v, (int, str, float, list, bool))}

            resp = connection.action(args.method, url, data=data, files=files)
            try:
                print(json.dumps(resp.json(), indent=4))
            except:
                print(resp.status_code)


if __name__ == "__main__":
    command = Command()
    command.run()
