import io
import re
import json
import argparse
import gzip
import xml.sax
import sys
import csv
from pyochre.primary_sources import Processor

csv.field_size_limit(1000000)

default_dialect = {
  "encoding": "utf-8",
  "lineTerminators": ["\r\n", "\n"],
  "quoteChar": "\"",
  "doubleQuote": True,
  "skipRows": 0,
  "commentPrefix": "#",
  "header": True,
  "headerRowCount": 1,
  "delimiter": ",",
  "skipColumns": 0,
  "skipBlankRows": False,
  "skipInitialSpace": False,
  "trim": False
}


class XsvProcessor(Processor):

    def generate_events(self, fd):
        header = self.schema.get(
            "metadata",
            {}
        ).get(
            "header",
            False
        )
        delimiter = self.schema.get(
            "metadata",
            {}
        ).get(
            "delimiter",
            self.default_delimiter
        )
        c = csv.DictReader(
            fd,
            delimiter=delimiter
        ) if header else csv.reader(
            fd,
            delimiter=delimiter
        )
        yield ("start", "document", {}, None)
        for i, row in enumerate(c, 1):
            yield ("start", "row", {"id" : i}, None)
            for k, v in row.items() if header else enumerate(row, 1):
                if v.strip() != "" or True:
                    yield ("start", "cell", {"id" : k, "value" : v}, None)
                    yield ("end", "cell", {}, None)
            yield ("end", "row", {}, None)
        yield ("end", "document", {}, None)        


class CsvProcessor(XsvProcessor):
    default_delimiter = ","


class TsvProcessor(XsvProcessor):
    default_delimiter = "\t"
    
