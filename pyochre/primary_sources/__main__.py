import logging
import os
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

def delete_primary_source(config, args, connection):
    obj = connection.get_object("primarysource", args.name)
    connection.delete(obj["url"])

def list_primary_sources(config, args, connection):
    logger.info("Primary sources:")
    for primarysource in connection.get_objects("primarysource")["results"]:
        logger.info("%d: %s", primarysource["id"], primarysource["name"])

def convert_primary_sources(config, args, connection):
    with open(args.schema, "rt") as ifd:
        schema = json.loads(ifd.read())

    if args.replace:
        connection.create_or_replace_object(
            model_name="primarysource",
            object_name=args.name,
            data={"name" : args.name}
        )
    else:
        connection.create_or_update_object(
            model_name="primarysource",
            object_name=args.name,
            data={"name" : args.name}
        )

    with formats[args.input_format](
            args.name,
            schema,
            domain_file=args.domain_file,
            data_file=args.data_file,
            materials_file=args.materials_file,
            connection=connection,
            replace=args.replace,
            enrich=args.enrich,
            base_path=args.base_path,
            upload_materials=args.upload_materials
    ) as proc:
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
        convert_parser.add_argument("--name", dest="name", required=True, help="Primary source name")
        convert_parser.add_argument("--schema", dest="schema", help="Schema for conversion")
        convert_parser.add_argument("--replace", dest="replace", action="store_true", default=False, help="If the file or REST object exists, replace it")
        convert_parser.add_argument("--upload_materials", dest="upload_materials", action="store_true", default=False, help="Upload materials (images, etc)")
        convert_parser.add_argument("--enrich", dest="enrich", action="store_true", default=False, help="If set, try to augment any WikiData references")
        convert_parser.add_argument("--base_path", dest="base_path", help="Base path", default=os.getcwd())        
        delete_parser = self.subparsers.add_parser(
            "delete",
            help="Delete a primary source from the server"            
        )
        delete_parser.add_argument("--name", dest="name", required=True)
        delete_parser.set_defaults(func=delete_primary_source)


if __name__ == "__main__":
    PrimarySourcesCommand().run()
