import logging
import os
import json
import gzip
import csv
from pyochre.utils import Command, meta_open


logger = logging.getLogger(__name__)


def create_csv_corpus(args, connection):
    with meta_open(args.metadata, "rt") as ifd:
        for row in csv.DictReader(ifd, delimiter="\t"):
            print(row)


class TwitterCommand(Command):
    
    def __init__(self):
        super(TwitterCommand, self).__init__(
            prog="python -m pyochre.extensions.twitter"
        )
        create_csv_corpus_parser = self.subparsers.add_parser(
            "create_csv_corpus",
            help=""
        )
        create_csv_corpus_parser.set_defaults(func=create_csv_corpus)
        create_csv_corpus_parser.add_argument(
            "--twitter_path",
            dest="twitter_path",
            required=True,
            help="Path to Twitter mirror"
        )
        create_csv_corpus_parser.add_argument(
            "--output",
            dest="output",
            required=True,
            help="CSV file to save corpus as"
        )


if __name__ == "__main__":
    TwitterCommand().run()
