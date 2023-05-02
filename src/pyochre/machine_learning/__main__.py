import logging
import tempfile
import os
import shutil
import os.path
from glob import glob
import re
from pyochre.utils import Command, meta_open
#from .mar import create_huggingface_mar, create_mar, create_topicmodel_mar


logger = logging.getLogger("pyochre.machine_learning")


def list_machine_learning_models(args, connection):
    logger.info("Machine learning models:")
    for machinelearningmodel in connection.get_objects("machinelearningmodel")["results"]:
        logger.info("%s", machinelearningmodel["name"])

def delete_machine_learning_model(args, connection):
    obj = connection.get_object("machinelearningmodel", args.name)
    connection.delete(obj["url"])

def import_mar_model(args, connection):
    pass

def import_huggingface_model(args, connection):
    obj = connection.create_or_replace_object(
        model_name="machinelearningmodel",
        object_name=args.name,        
        data={"name" : args.name, "huggingface_name" : args.huggingface_name}
    )

def train_starcoder_model(args, connection):
    pass

def train_topic_model(args, connection):
    query = connection.get_object("query", args.query_name)
    primarysource = connection.get_object("primarysource", args.primary_source_name)
    obj = connection.create_or_replace_object(
        model_name="machinelearningmodel",
        object_name=args.name,        
        data={
            "name" : args.name,
            "query" : query["id"],
            "primarysource" : primarysource["id"],
            "lowercase" : args.lowercase,
            "topic_count" : args.topic_count,
        },
    )

    #if not args.replace:
    #    connection.delete_object("machinelearningmodel", args.name)    
    # connection.invoke(
    #     "machinelearningmodel/create/topic_model/",
    #     data={
    #         "name" : args.name,
    #         "query" : query["id"],
    #         "primarysource" : primarysource["id"],
    #         "lowercase" : args.lowercase,
    #         "topic_count" : args.topic_count,
    #     },
    # )

def apply_model(args, connection):
    machinelearningmodel = connection.get_object("machinelearningmodel", args.model_name)
    #query = connection.get_object("query", args.query_name)
    primarysource = connection.get_object("primarysource", args.primary_source_name)
    
    connection.create_or_replace_object(
        #model["apply_url"],
        model_name="annotation",
        object_name=args.name,
        data={
            #"name" : args.name,
            #"query" : query["url"],
            "primarysource" : primarysource["url"],
            "machinelearningmodel" : machinelearningmodel["url"]
        }
    )
    #print(model)
    #connection.invoke(
    #    "machinelearningmodel/create/topic_model/",
    #    data={
    #        "name" : args.name,
    #        "query" : query["id"],
    #        "primarysource" : primarysource["id"]
    #    },
    #)
    
def create_machine_learning_model(args, connection):
    data = {"name" : args.name}
    files = {}
    tdir = tempfile.mkdtemp()
    mar = os.path.join(tdir, "model.mar")
    sig = os.path.join(tdir, "signature.ttl")
    try:        
        with open(sig, "wt") as ofd:
            with meta_open(args.signature_file, "rt") as ifd:
                ofd.write(ifd.read())
        if args.mar_file:
            with open(mar, "wb") as ofd:
                with meta_open(args.mar_file, "rb") as ifd:
                    ofd.write(ifd.read())
        elif args.huggingface_model_name:
            create_huggingface_mar(
                mar,
                args.huggingface_model_name,
                args.ochre_path,
                args.handler_file
            )
        elif args.topic_model_query:
            create_topicmodel_mar(
                mar,
                args.topic_model_query,
                args.topic_count,
                connection,
                tdir,
                args.name,
                args.handler_file
            )
        else:
            create_mar(mar, args)
        files = {
            "mar_file" : mar,
            "signature_file" : sig
        }
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
        
    except Exception as e:
        raise e
    finally:
        for fname in glob(os.path.join(tdir, "*")):            
            os.remove(fname)
        shutil.rmtree(tdir)
    #with 
    #if args.mar_url:
    #    data["mar_url"] = args.mar_url
    #elif args.mar_file:            
    #    files["mar_file"] = args.mar_file
    #elif args.huggingface_model_name:
    #    pass
    #    #files["mar_file"] = create_huggingface_mar(arg)
    #else:
    #    files["mar_file"] = create_mar(args)
    #if re.match(r"^https?://.*$", args.signature_file):
    #    data["signature_url"] = args.signature_file
    #else:
    #    files["signature_file"] = args.signature_file


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

        apply_model_parser = self.subparsers.add_parser(
            "apply_model",
            help="Apply the model to a query on a primary source"
        )
        apply_model_parser.set_defaults(func=apply_model)
        apply_model_parser.add_argument(
            "--query_name",
            dest="query_name",
            required=False
        )
        apply_model_parser.add_argument(
            "--primary_source_name",
            dest="primary_source_name",
            required=True
        )
        apply_model_parser.add_argument(
            "--model_name",
            dest="model_name",
            required=True
        )        
        apply_model_parser.add_argument(
            "--name",
            dest="name",
            required=True
        )
        apply_model_parser.add_argument(
            "--user",
            dest="user",
            required=False
        )
        
        create_parser = self.subparsers.add_parser(
            "create",
            help="Create a new model on the server"
        )
        create_parser.add_argument(
            "--name",
            dest="name",
            required=True
        )
        create_parser.add_argument(
            "--replace",
            dest="replace",
            action="store_true",
            default=False,
            help="If the file or REST object exists, replace it"
        )
        create_subparsers = create_parser.add_subparsers()

        create_mar_parser = create_subparsers.add_parser(
            "mar",
            help="Create a model from a MAR file."
        )
        create_mar_parser.set_defaults(func=import_mar_model)
        create_mar_parser.add_argument(
            "--mar_file",
            dest="mar_file"
        )
        
        create_topic_model_parser = create_subparsers.add_parser(
            "topic_model",
            help="Train a new topic model."
        )
        create_topic_model_parser.set_defaults(func=train_topic_model)
        create_topic_model_parser.add_argument(
            "--lowercase",
            dest="lowercase",
            default=False,
            action="store_true"
        )
        create_topic_model_parser.add_argument(
            "--query_name",
            dest="query_name",
            required=True
        )
        create_topic_model_parser.add_argument(
            "--primary_source_name",
            dest="primary_source_name",
            required=True
        )
        #create_topic_model_parser.add_argument(
        #    "--name",
        #    dest="name",
        #    required=True
        #)
        create_topic_model_parser.add_argument(
            "--topic_count",
            dest="topic_count",
            default=10,
            type=int
        )
        #create_topic_model_parser.add_argument(
        #    "--replace",
        #    dest="replace",
        #    action="store_true",
        #    default=False,
        #    help="If the file or REST object exists, replace it"
        #)
        
        create_huggingface_parser = create_subparsers.add_parser(
            "huggingface",
            help="Import a Huggingface model."
        )
        create_huggingface_parser.set_defaults(func=import_huggingface_model)
        create_huggingface_parser.add_argument(
            "--huggingface_name",
            dest="huggingface_name",
            help="Name of the Huggingface model (e.g. 'microsoft/GPT')"
        )
        create_huggingface_parser.add_argument(
            "--keep_repo",
            dest="keep_repo",
            default=False,
            action="store_true",
            help="Don't delete a cloned HuggingFace repository between runs (useful for debugging without wasting bandwidth/time)"
        )

        create_starcoder_parser = create_subparsers.add_parser(
            "starcoder",
            help="Train a new StarCoder model."
        )                
        create_starcoder_parser.set_defaults(func=train_starcoder_model)
        
        #create_parser.add_argument(
        #    "--topic_model_query",
        #    dest="topic_model_query"
        #)
        #create_parser.add_argument(
        #    "--handler_file",
        #    dest="handler_file"
        #)
        #create_parser.add_argument(
        #    "--model_file",
        #    dest="model_file"
        #)
        #create_parser.add_argument(
        #    "--signature_file",
        #    dest="signature_file"
        #)
        #create_parser.add_argument(
        #    "--topic_count",
        #    dest="topic_count",
        #    default=10,
        #    type=int
        #)
        #create_parser.add_argument(
        #    "--enrich",
        #    dest="enrich",
        #    action="store_true",
        #    default=False,
        #    help="If set, try to augment any WikiData references"
        #)
        #create_parser.set_defaults(
        #    func=create_machine_learning_model
        #)
        delete_parser = self.subparsers.add_parser(
            "delete",
            help="Delete a machine learning model from the server"
        )
        delete_parser.add_argument(
            "--name",
            dest="name",
            required=True
        )
        delete_parser.add_argument(
            "--user",
            dest="user",
            required=False
        )
        delete_parser.set_defaults(
            func=delete_machine_learning_model
        )


if __name__ == "__main__":
    MachineLearningCommand().run()
