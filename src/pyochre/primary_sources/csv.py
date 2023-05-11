import io
import re
import json
import argparse
import gzip
import xml.sax
import xml.sax.saxutils
import sys
import csv
from lxml.etree import XMLParser, TreeBuilder

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


class XsvParser(TreeBuilder):
    
    def __call__(self, fd, limit=100000, split=False):
        c = csv.DictReader(
            fd,
            delimiter=self.delimiter
        ) if self.header else csv.reader(
            fd,
            delimiter=self.delimiter
        )
        self.start("document", {})
        for i, row in enumerate(c, 1):
            if limit and i > limit:
                break
            self.start("row", {"id" : str(i)})
            for k, v in row.items() if self.header else enumerate(row, 1):
                if v and v.strip() != "":
                    if not isinstance(v, str):
                        v = v.decode("utf-8")
                    self.start("cell", {"id" : str(k), "value" : str(v)})
                    self.end("cell")
            self.end("row")
        self.end("document")
        yield self.close()


class CsvParser(XsvParser):
    delimiter = ","
    header = True

class NoHeaderCsvParser(XsvParser):
    delimiter = ","
    header = False    

class TsvParser(XsvParser):
    delimiter = "\t"
    header = True

class NoHeaderTsvParser(XsvParser):
    delimiter = "\t"
    header = False
    
