import logging
import re
import os
import json
import gzip
import zipfile
import csv
from pairtree import PairtreeStorageFactory
from django.conf import settings
from pyochre.utils import Command, meta_open


logger = logging.getLogger(__name__)


def create_csv_corpus(args, connection):
    psf = PairtreeStorageFactory()
    with meta_open(args.collection_file, "rt") as ifd, meta_open(args.output, "wt") as ofd:
        itsv = csv.DictReader(ifd, delimiter="\t")
        otsv = csv.DictWriter(ofd, itsv.fieldnames + ["full_content"], delimiter="\t")
        otsv.writeheader()
        for row in itsv:
            toks = row["htid"].split(".")
            subcollection = toks[0]
            ident = ".".join(toks[1:])
            try:            
                store = psf.get_store(
                    store_dir=os.path.join(
                        args.hathi_trust_path,
                        subcollection
                    ),
                    uri_base=settings.OCHRE_NAMESPACE
                )

                obj = store.get_object(ident, create_if_doesnt_exist=False)
            except:
                continue
            full_content = []
            for subpath in obj.list_parts():
                for fname in obj.list_parts(subpath):
                    if fname.endswith("zip"):
                        with zipfile.ZipFile(
                                obj.get_bytestream(
                                    "{}/{}".format(subpath, fname),
                                    streamable=True
                                )
                        ) as izf:                            
                            for page in sorted(izf.namelist()):
                                if page.endswith("txt"):
                                    txt = izf.read(page).decode("utf-8")
                                    if args.correct_line_breaks:
                                        txt = re.sub(r"\-\s*?\n\s*", "", txt)
                                    full_content.append(txt)
                                    
            full_content = "\n".join(full_content)
            row["full_content"] = full_content.replace("\n", " ")
            #if args.max_content_length <= 0 else full_content[0:args.max_content_length]
            otsv.writerow(row)


class HathiTrustCommand(Command):
    
    def __init__(self):
        super(HathiTrustCommand, self).__init__(
            prog="python -m pyochre.extensions.hathi_trust"
        )
        create_csv_corpus_parser = self.subparsers.add_parser(
            "create_csv_corpus",
            help="This command requires a local copy of the HathiTrust master index (a TSV file) and mirror of the corpus itself."
        )
        create_csv_corpus_parser.set_defaults(func=create_csv_corpus)
        create_csv_corpus_parser.add_argument(
            "--collection_file",
            dest="collection_file",
            required=True,
            help="Path to HathiTrust Collection TSV file"
        )
        create_csv_corpus_parser.add_argument(
            "--hathi_trust_path",
            dest="hathi_trust_path",
            required=True,            
            help="Path to the root of the HathiTrust mirror"
        )
        create_csv_corpus_parser.add_argument(
            "--output",
            dest="output",
            required=True,
            help="CSV file to save corpus as"
        )
        # create_csv_corpus_parser.add_argument(
        #     "--max_content_length",
        #     dest="max_content_length",
        #     type=int,
        #     default=0,
        #     help="Maximum characters to include from content"
        # )
        create_csv_corpus_parser.add_argument(
            "--correct_line_breaks",
            dest="correct_line_breaks",
            default=False,
            action="store_true",
            help="If a dash occurs at the end of a line, remove the dash and connect the end of the line to the beginning of the next"
        )


if __name__ == "__main__":
    HathiTrustCommand().run()
