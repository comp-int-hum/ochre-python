import logging
import argparse
import re
import os.path
import zipfile
import csv
from pairtree import PairtreeStorageFactory
from pyochre.utils import meta_open


logger = logging.getLogger(__name__)


def create_csv_corpus(hathi_trust_path, collection_file, correct_line_breaks, output):
    psf = PairtreeStorageFactory()
    with meta_open(collection_file, "rt") as ifd, meta_open(output, "wt") as ofd:
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
                        hathi_trust_path,
                        subcollection
                    )
                )
                obj = store.get_object(ident, create_if_doesnt_exist=False)
            except:
                logger.error(
                    "Could not access HathiTrust document '%s'",
                    row["htid"]
                )
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
                                    if correct_line_breaks:
                                        txt = re.sub(r"\-\s*?\n\s*", "", txt)
                                    full_content.append(txt)
                                    
            full_content = "\n".join(full_content)
            row["full_content"] = full_content.replace("\n", " ")
            #if args.max_content_length <= 0 else full_content[0:args.max_content_length]
            otsv.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="python -m pyochre.extensions.hathi_trust",
    )
    parser.add_argument(
        "--collection_file",
        dest="collection_file",
        required=True,
        help="Path to HathiTrust Collection TSV file"
    )
    parser.add_argument(
        "--hathi_trust_path",
        dest="hathi_trust_path",
        required=True,            
        help="Path to the root of the HathiTrust mirror"
    )
    parser.add_argument(
        "--output",
        dest="output",
        required=True,
        help="CSV file to save corpus as"
    )
    parser.add_argument(
        "--correct_line_breaks",
        dest="correct_line_breaks",
        default=False,
        action="store_true",
        help="If a dash occurs at the end of a line, remove the dash and connect the end of the line to the beginning of the next"
    )
    args = parser.parse_args()

    create_csv_corpus(
        args.hathi_trust_path,
        args.collection_file,
        args.correct_line_breaks,
        args.output
    )
