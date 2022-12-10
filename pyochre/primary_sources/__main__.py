import logging
import json
import tarfile
from pyochre.utils import Command, meta_open
from pyochre.primary_sources import TsvProcessor, CsvProcessor, XmlProcessor


logger = logging.getLogger("pyochre.primary_sources")


formats = {
    "csv" : CsvProcessor,
    "tsv" : TsvProcessor,
    "xml" : XmlProcessor,
}


def list_primary_sources(config, args, connection):
    logger.info("Primary sources:")
    for primarysource in connection.get_objects("primarysource")["results"]:
        logger.info("%s", primarysource["name"])


def convert_primary_sources(config, args, connection):
    with open(args.schema, "rt") as ifd:
        schema = json.loads(ifd.read())

    with formats[args.input_format](
            args.name,
            schema,
            domain_file=args.domain_file,
            data_file=args.data_file,
            materials_file=args.materials_file,
            connection=connection,
            replace=args.replace
    ) as proc:
        existing = None
        for ps in connection.get_objects("primarysource")["results"]:
            if ps["name"] == args.name and ps["creator"] == config["user"]:
                existing = ps["url"]
                
        if args.replace and existing:
            connection.delete(ps["url"])
            connection.create("primarysource", {"name" : args.name})
        elif not existing:
            connection.create("primarysource", {"name" : args.name})
        if args.input_file.endswith("tgz") or args.input_file.endswith("tar.gz"):
            with tarfile.open(args.input_file, "r:gz") as tfd:
                for member in tfd.getmembers():
                    if member.isfile():
                        proc(tfd.extractfile(member))
        else:
            with meta_open(args.input_file, "rt") as ifd:
                proc(ifd)


# CSV XML TEI JSONL         
class PrimarySourcesCommand(Command):
    
    def __init__(self):
        super(PrimarySourcesCommand, self).__init__(prog="python -m pyochre.primary_sources")
        list_parser = self.subparsers.add_parser("list", help="Print information about primary sources on the server")
        list_parser.set_defaults(func=list_primary_sources)
        convert_parser = self.subparsers.add_parser("convert", help="Convert input files to primary source files")
        convert_parser.set_defaults(func=convert_primary_sources)
        convert_parser.add_argument("--domain_file", dest="domain_file", help="File to save domain RDF to")
        convert_parser.add_argument("--data_file", dest="data_file", help="File to save data RDF to")
        convert_parser.add_argument("--materials_file", dest="materials_file", help="Zip file to save materials to")
        convert_parser.add_argument("--input_file", dest="input_file", help="Input file")
        convert_parser.add_argument("--input_format", dest="input_format", help="Format of input file", choices=formats.keys())
        convert_parser.add_argument("--name", dest="name", help="Primary source name")
        convert_parser.add_argument("--schema", dest="schema", help="Schema for conversion")
        convert_parser.add_argument("--replace", dest="replace", action="store_true", default=False, help="If the file or REST object exists, replace it")
        
if __name__ == "__main__":
    PrimarySourcesCommand().run()
