import argparse
import os.path
import os
import logging
from getpass import getpass
from dotenv import load_dotenv, dotenv_values
from pyochre.rest import Connection


logger = logging.getLogger("pyochre.rest")


def dummy(args, connection):
    logger.warning("A Command object was invoked without its default function being overridden")


class Command(object):
    connection = None
    
    def __init__(self, prog=None):
        self.parser = argparse.ArgumentParser(
            prog=prog,
        )
        self.parser.add_argument("--ochre_config", dest="ochre_config", default=os.path.expanduser("~/ochre/env"))
        self.parser.add_argument("--ochre_path", dest="ochre_path", default=os.path.expanduser("~/ochre"))
        self.parser.add_argument("--protocol", dest="protocol", default="http")
        self.parser.add_argument("--hostname", dest="hostname", default="localhost")
        self.parser.add_argument("--port", dest="port", type=int, default=8000)
        self.parser.add_argument("--path", dest="path", default="/api")
        self.parser.add_argument("--user", dest="user", default=None)
        self.parser.add_argument("--password", dest="password", action="store_true", default=None)
        self.parser.add_argument("--log_level", dest="log_level", default="WARNING", choices=["INFO", "WARNING", "DEBUG", "ERROR", "CRITICAL", "NOTSET"])
        self.parser.set_defaults(func=dummy)
        self.subparsers = self.parser.add_subparsers()
        
    def run(self):
        args = self.parser.parse_args()

        logging.basicConfig(level=getattr(logging, args.log_level))
        
        if args.password:
            args.password = getpass("Enter password: ")

        for k, v in dotenv_values(args.ochre_config).items():
            if getattr(args, k, None) == None:                
                setattr(args, k.lower() if k in ["USER", "PASSWORD", "HOSTNAME", "PORT", "PROTOCOL"] else k, v)

        connection = Connection(vars(args))

        args.func(args, connection)
    
    

