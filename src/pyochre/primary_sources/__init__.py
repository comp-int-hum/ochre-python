from .csv import CsvParser, TsvParser, NoHeaderCsvParser, NoHeaderTsvParser
from .xml import XmlParser
from .json import JsonParser, JsonLineParser
from .domain import create_domain
from .wikidata import enrich_uris
parsers = {
    "csv" : CsvParser,
    "tsv" : TsvParser,
    "ncsv" : NoHeaderCsvParser,
    "ntsv" : NoHeaderTsvParser,    
    "xml" : XmlParser,
    "json" : JsonParser,
    "jsonl" : JsonLineParser,
}
