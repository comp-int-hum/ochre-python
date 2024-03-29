import io
import re
import json
import argparse
import gzip
import xml.sax
from xml.sax.saxutils import quoteattr, escape
import sys
import csv
from lxml.etree import XMLParser, TreeBuilder
import unicodedata

def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

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
    
    def __call__(self, fd, split=False):
        c = csv.DictReader(
            fd,
            delimiter=self.delimiter
        ) if self.header else csv.reader(
            fd,
            delimiter=self.delimiter
        )        

        self.start("document", {})
        for i, row in enumerate(c, 1):
            if split and (i - 1) % 10000 == 0:
                if i != 1:
                    self.end("document")
                    yield self.close()                    
                    self.start("document", {})
            self.start("row", {"id" : str(i)})
            for k, v in row.items() if self.header else enumerate(row, 1):
                if v and v.strip() != "":
                    if not isinstance(v, str):
                        v = v.decode("utf-8")
                    try:                        
                        self.start("cell", {"id" : k, "value" : remove_control_characters(v)})
                        self.end("cell")
                    except Exception as e:
                        
                        with open("error.txt", "wt") as ofd:
                            ofd.write(quoteattr(v))
                        raise e
                        
#except Exception as e:
#                        print(k, v, quoteattr(k), quoteattr(v))
#                        raise e
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
    
