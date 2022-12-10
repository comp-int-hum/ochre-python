import argparse
import os.path
import os
import logging
from getpass import getpass
from pyochre.rest import Connection
from pyochre.utils import Config

logger = logging.getLogger("pyochre.rest")

def dummy(config, args, connection):
    logger.warning("A Command object was invoked without its default function being overridden")

class Command(object):
    connection = None
    
    def __init__(self, prog=None):
        self.parser = argparse.ArgumentParser(
            prog=prog,
        )
        self.parser.add_argument("--protocol", dest="protocol", default="http")
        self.parser.add_argument("--hostname", dest="hostname", default="localhost")
        self.parser.add_argument("--port", dest="port", type=int, default=8080)
        self.parser.add_argument("--path", dest="path", default="/api")
        self.parser.add_argument("--user", dest="user", default="user1")
        self.parser.add_argument("--password", dest="password", action="store_true", default=False)
        self.parser.add_argument("--store_settings", dest="store_settings", action="store_true", default=False)
        self.parser.add_argument("--log_level", dest="log_level", default="INFO", choices=["INFO", "WARNING", "DEBUG", "ERROR", "CRITICAL", "NOTSET"])
        self.parser.set_defaults(func=dummy)
        self.subparsers = self.parser.add_subparsers()

    def run(self):
        args = self.parser.parse_args()

        logging.basicConfig(level=getattr(logging, args.log_level))

        if args.password:
            args.password = getpass("Enter password: ")
        
        with Config(**vars(args), mode="rw" if args.store_settings else "r") as config:
            try:
                connection = Connection(config)
            except:
                logger.warn("Couldn't connect or authenticate with server, so REST actions not available")
                connection = False
            args.func(config, args, connection)
        

    
    

