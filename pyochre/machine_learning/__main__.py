import logging
import re
from pyochre.utils import Command
from .mar import create_huggingface_mar, create_mar


logger = logging.getLogger("pyochre.machine_learning")


def list_machine_learning_models(config, args, connection):
    logger.info("Machine learning models:")
    for machinelearningmodel in connection.get_objects("machinelearningmodel")["results"]:
        logger.info("%s", machinelearningmodel["name"])

def delete_machine_learning_model(config, args, connection):
    obj = connection.get_object("machinelearningmodel", args.name)
    connection.delete(obj["url"])
        
def create_machine_learning_model(config, args, connection):
    data = {"name" : args.name}
    files = {}
    if args.mar_url:
        data["mar_url"] = args.mar_url
    elif args.mar_file:            
        files["mar_file"] = args.mar_file
    elif args.huggingface_model_name:
        pass
        #files["mar_file"] = create_huggingface_mar(args)
    else:
        files["mar_file"] = create_mar(args)
    if re.match(r"^https?://.*$", args.signature_file):
        data["signature_url"] = args.signature_file
    else:
        files["signature_file"] = args.signature_file
    if args.replace:
        connection.create_or_replace_object(
            model_name="machinelearningmodel",
            object_name=args.name,
            data=data,
            files=files
        )
    else:
        connection.create_or_update_object(
            model_name="machinelearningmodel",
            object_name=args.name,
            data=data,
            files=files
        )


class MachineLearningCommand(Command):
    
    def __init__(self):
        super(MachineLearningCommand, self).__init__(
            prog="python -m pyochre.machine_learning"
        )
        list_parser = self.subparsers.add_parser(
            "list",
            help="Print information about machine learning models on the server"
        )
        list_parser.set_defaults(func=list_machine_learning_models)
        create_parser = self.subparsers.add_parser(
            "create",
            help="Create a new model on the server"
        )
        create_parser.add_argument("--mar_url", dest="mar_url")
        create_parser.add_argument("--mar_file", dest="mar_file")
        create_parser.add_argument("--huggingface_model_name", dest="huggingface_model_name")
        create_parser.add_argument("--signature_file", dest="signature_file")
        create_parser.add_argument("--name", dest="name", required=True)
        create_parser.add_argument("--replace", dest="replace", action="store_true", default=False, help="If the file or REST object exists, replace it")
        create_parser.add_argument("--enrich", dest="enrich", action="store_true", default=False, help="If set, try to augment any WikiData references")
        create_parser.add_argument("--keep_repo", dest="keep_repo", default=False, action="store_true", help="Don't delete a cloned HuggingFace repository between runs (useful for debugging without wasting bandwidth/time)")
        create_parser.set_defaults(func=create_machine_learning_model)
        delete_parser = self.subparsers.add_parser(
            "delete",
            help="Delete a machine learning model from the server"            
        )
        delete_parser.add_argument("--name", dest="name", required=True)
        delete_parser.set_defaults(func=delete_machine_learning_model)


if __name__ == "__main__":
    MachineLearningCommand().run()
