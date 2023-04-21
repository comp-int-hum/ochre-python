import logging
from pyochre.utils import Command
from pyochre.rest import Connection, fixtures


logger = logging.getLogger("pyochre.rest")


def info(args, connection):
    logger.info("End-points")
    for endpoint_name, endpoint_url in connection.endpoints.items():
        logger.warning(
            "'%s' endpoint is '%s'",
            endpoint_name,
            endpoint_url
        )


def list_objects(args, connection):
    logger.info("Models and objects")
    for endpoint_name, endpoint_url in connection.endpoints.items():
        logger.warning(
            "'%s' endpoint is '%s'",
            endpoint_name,
            endpoint_url
        )
        for obj in connection.get_objects(endpoint_name)["results"]:
            logger.warning("%s", obj.get("name", "") + obj.get("username", ""))


def create_objects(args, connection):
    plan = fixtures.create_plan(args.fixture_files, args, connection)
    fixtures.perform_plan(plan, args, connection)
    #print(plan)


def wipe_objects(args, connection):
    for model in set([item["model"] for item in order]):
        existing_items = connection.get_objects(model)["results"]
        logger.info("Deleting %d existing objects of model '%s'", len(existing_items), model)            
        for item in existing_items:
            connection.delete(item["url"])


class RestCommand(Command):
    def __init__(self):
        super(RestCommand, self).__init__(prog="python -m pyochre.rest")
        info_parser = self.subparsers.add_parser("info", help="Print information about the REST server")
        info_parser.set_defaults(func=info)
        list_parser = self.subparsers.add_parser("list", help="List visible objects of each type")
        list_parser.set_defaults(func=list_objects)                
        create_parser = self.subparsers.add_parser("create", help="Create the objects in the specified fixture files")
        create_parser.add_argument(
            "--fixture_files",
            dest="fixture_files",
            nargs="*",
            help="Fixture files specifying objects in JSON format",
            default=[]
        )
        create_parser.add_argument(
            "--skip_models",
            dest="skip_models",
            nargs="*",
            help="List of models to skip",
            default=[]
        )
        create_parser.add_argument(
            "--skip_objects",
            dest="skip_objects",
            nargs="*",
            help="List of object names to skip",
            default=[]
        )
        create_parser.add_argument(
            "--delete",
            dest="delete",
            default=False,
            action="store_true",
            help="Delete any existing objects that clash with the fixtures"
        )
        create_parser.add_argument(
            "--file_paths",
            dest="file_paths",
            nargs="*",
            default=[],
            help="Locations to search for files"
        )
        create_parser.set_defaults(func=create_objects)
        

if __name__ == "__main__":
    RestCommand().run()
