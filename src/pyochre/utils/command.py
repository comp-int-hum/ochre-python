import json
import argparse
import re
import os.path
import os
import logging
from getpass import getpass
#from dotenv import load_dotenv, dotenv_values
from pyochre.rest import Connection
from pyochre import env
#import environ


logger = logging.getLogger("pyochre.rest")


def dummy(args, connection):
    logger.warning("A Command object was invoked without its default function being overridden")


class Command(object):
    connection = None
    
    def __init__(self, prog=None):
        env.read_env(env("ENVIRONMENT"))
        self.parser = argparse.ArgumentParser(
            prog="python -m pyochre",
        )
        
    def run(self):
        logging.basicConfig(level=getattr(logging, env("LOG_LEVEL")))
        connection = Connection()
        self.subparsers = self.parser.add_subparsers()

        #print(connection.openapi["paths"]["/api/annotation/create_human_annotation/"])
        #print(connection.openapi["components"]["schemas"]["HumanAnnotation"])
        for obj in connection.openapi["components"]["schemas"].keys():
            if obj in ["ContentType"]:
                continue
            actions = []
            for path, methods in connection.openapi["paths"].items():
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
                ssps = sp.add_subparsers()
                for path, methods in actions:
                    for method_name, method in methods.items():
                        ssp = ssps.add_parser(
                            re.sub(obj.lower() + "s?$", "", method["operationId"]),
                            help=method["description"]
                        )
                        ssp.set_defaults(
                            url=path,
                            method=method_name
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
                        #print(connection.openapi["components"]["schemas"])
                        
                        if rb:
                            schema = connection.openapi["components"]["schemas"][os.path.split(rb)[-1]]
                            for prop_name, prop in schema["properties"].items():
                                pass
                                #ssp.add_argument(
                                #    "--{}".format(prop_name),
                                #    dest=prop_name
                                #)
                            #print(schema)
                        #requestBody
                        for param in method["parameters"]:
                            tp = param["schema"]["type"]
                            ssp.add_argument(
                                "--{}".format(param["name"]),
                                dest=param["name"],
                                required=param.get("required", False),
                                help=param["description"]
                            )
                            pass
                        #print(path, method_name, method)
        args = self.parser.parse_args()

        #args.func(args, connection)


        
    

