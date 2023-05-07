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


logger = logging.getLogger("pyochre")


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
        self.object_fields = {}
        self.namespace = connection.openapi["info"]["namespace"]
        list_urls = {}
        for obj in connection.openapi["components"]["schemas"].keys():
            if obj in ["ContentType"]:
                continue
            actions = []
            for path, methods in connection.openapi["paths"].items():
                path = "{}://{}:{}{}".format(env("PROTOCOL"), env("HOSTNAME"), env("PORT"), path)
                relevant = False
                for method, method_info in methods.items():
                    
                    for code, code_info in method_info["responses"].items():
                        robj = os.path.split(                            
                            code_info.get(
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
                        )[-1]
                        if obj == robj:
                            relevant = True
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
                        action_name = re.sub(obj.lower() + "s?$", "", method["operationId"])
                        ssp = ssps.add_parser(
                            action_name,
                            help=method["description"],
                            formatter_class=argparse.ArgumentDefaultsHelpFormatter
                        )
                        if action_name == "list":
                            list_urls[obj] = path
                            sp.set_defaults(
                                url=path,
                                method="get"
                            )
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
                                    if (tp == "array" and prop["items"].get("format") == "object"):
                                        self.object_fields[(action_name, prop_name)] = prop["items"]["discriminator"]
                                    elif prop.get("format") == "object" and "discriminator" in prop:
                                        self.object_fields[(action_name, prop_name)] = prop["discriminator"]            
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
                            else:
                                                        ssp.add_argument(
                                "--{}".format(param["name"]),
                                dest=param["name"],
                                required=param.get("required", False),
                                help=param["description"]
                            )
        args = self.parser.parse_args()        
        vargs = vars(args)
        for k in list(vargs.keys()):
            key = (vargs.get("action_name"), k)            
            if key in self.object_fields:
                success = False
                model = self.object_fields[key]
                if not vargs[k]:
                    continue
                toks = vargs[k].split(":")
                if len(toks) == 2:
                    name, user = toks
                else:
                    name = toks[0]
                    user = env("USER")
                resp = connection.action("get", list_urls[model])
                for x in resp.json()["results"]:
                    if x["creator"] == user and x["name"] == name:
                        vargs[k] = x["url"]
                        success = True
                if not success:
                    raise Exception("Could not find {} matching name {} and creator {}".format(model, name, user))

        
        if "object_name" in vargs:
            obj = None
            for res in connection.action("get", list_urls[vargs["object_type"]]).json()["results"]:
                if res["name"] == vargs["object_name"] and res["creator"] == vargs["object_creator"]:
                    obj = res
            if not obj:
                raise Exception(
                    "Could not find {} matching name {} and creator {}".format(
                        vargs["object_type"],
                        vargs["object_name"],
                        vargs["object_creator"],
                    )
                )
            url = obj["url"]
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
