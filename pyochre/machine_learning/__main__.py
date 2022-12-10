import logging
from pyochre.utils import Command


logger = logging.getLogger("pyochre.machine_learning")


def list_machine_learning_models(config, args, connection):
    logger.info("Machine learning models:")
    for machinelearningmodel in connection.get_objects("machinelearningmodel")["results"]:
        logger.info("%s", machinelearningmodel["name"])


# CSV XML TEI JSONL         
class MachineLearningCommand(Command):
    
    def __init__(self):
        super(MachineLearningCommand, self).__init__(prog="python -m pyochre.machine_learning")
        list_parser = self.subparsers.add_parser("list", help="Print information about machine learning models on the server")
        list_parser.set_defaults(func=list_machine_learning_models)


if __name__ == "__main__":
    MachineLearningCommand().run()
