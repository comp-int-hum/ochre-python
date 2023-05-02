import typing
import subprocess
import re
import io
import os.path
import shlex
import json
import zipfile
import pickle
from importlib.resources import files
from django.conf import settings
from pyochre.utils import rdf_store
from pyochre.server.ochre.models import PrimarySource
from rdflib import Graph

import logging
import sys
import io
import os
import json
import tarfile
from pyochre.server.ochre import settings
from pyochre.utils import meta_open
from pyochre.primary_sources import TsvParser, CsvParser, JsonParser, create_domain, enrich_uris, NoHeaderTsvParser, NoHeaderCsvParser, XmlParser
from lxml.etree import XML, XSLT, parse, TreeBuilder, tostring, XSLTExtension
import rdflib
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib import Dataset, Namespace, URIRef, Literal, BNode
from rdflib.graph import BatchAddGraph


logger = logging.getLogger(__name__)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func

formats = {
    "csv" : CsvParser,
    "tsv" : TsvParser,
    "ncsv" : NoHeaderCsvParser,
    "ntsv" : NoHeaderTsvParser,    
    "xml" : XmlParser,
    "json" : JsonParser,
    #"jsonl" : JsonlParser,
}

def file_type(fname):
    _, ext = os.path.splitext(re.sub(r"\.(gz|bz2)$", "", fname))
    return ext[1:]

@shared_task
def expand_primarysource(
        object_id,
        data_file,
        transformation_file,
        materials_file,
        split_data
):
    try:
        obj = PrimarySource.objects.get(id=object_id)
        
        logger.info("Load the XML-to-RDF transformation rules")
        with meta_open(transformation_file, "rt") as ifd:
            transform = XSLT(parse(ifd))

        logger.info("Instantiating the necessary X-to-XML parser")
        ft = file_type(data_file)
        parser = formats[ft]()

        logger.info("Creating XML from the original data")
        with meta_open(data_file, "rt") as ifd:
            for xml in parser(ifd, split=split_data):
        
                logger.info("Creating RDF from XML")
                tr = transform(xml)

                logger.info("Loading the RDF and skolemizing it")
                g = rdflib.Graph(base="http://test/")
                g.parse(data=tostring(tr), format="xml", publicID=OCHRE)
                g = g.skolemize()

                # create or replace the primary source graph on the RDF server
                #obj = connection.create_or_replace_object(
                #   model_name="primarysource",
                #   object_name=args.name,
                #   data={"name" : args.name}
                #)

                logger.info("Creating dataset handle from a SPARQL connection to the RDF server")
                store = rdf_store(settings=settings)
                dataset = Dataset(store=store, default_graph_base=OCHRE)

                logger.info("Getting the named graph corresponding to the primary source")
                ng = dataset.graph(
                    OCHRE["{}_data".format(obj.id)]
                )

                # information to collect
                uris = set()
                potential_materials = {}
                ignore = set()
                materials = {}

                # modalities = {
                #     OCHRE[x] : x for x in [
                #         "image",
                #         "video",
                #         "text",
                #         "audio",
                #         "tensor"
                #     ]
                # }

                #for s, p, o in g:
                #    if p in modalities:
                #        potential_materials[o] = modalities[p]

                #for uri, name in modalities.items():
                #    ng.add((uri, OCHRE["hasLabel"], Literal(name)))

                #for s, _, o in g.triples((None, OCHRE["hasLabel"], None)):
                #    if s in potential_materials:
                #        fname = os.path.join(args.base_path, o)
                #        if os.path.exists(fname):
                #            materials[s] = (fname, potential_materials[s])
                #        else:
                #            ignore.add(s)
                logger.info("Sending triples to the server")
                #ng.parse(data=g.serialize(format="turtle"), format="turtle")
                #every = 10000
                for i, (s, p, o) in enumerate(g):
                    #if s in ignore or o in ignore:
                    #    continue
                    #for n in [s, p, o]:
                    #    if isinstance(n, URIRef) and "wikidata" in n:
                    #        uris.add(n)
                    ng.add(
                        (
                            s,
                            p,
                            o
                        )
                    )
                #     break
                    #if i % every == 0:
                    #    store.commit()
                    #    print(i)
                #if i % every != 0:
                store.commit()

        dg = dataset.graph(
           OCHRE["{}_domain".format(obj.id)]
        )
        for s, p, o in create_domain(obj):
           dg.add((s, p, o))
        store.commit()

        # for uri, (fname, mode) in materials.items():
        #     ext = os.path.splitext(fname)[-1][1:]
        #     with open(fname, "rb") as ifd:
        #         connection.create_object(
        #             "material",
        #             {
        #                 "uid" : str(uri),
        #                 "content_type" : "{}/{}".format(mode, ext)
        #             },
        #             files={"file" : ifd}
        #         )
        obj.state = obj.COMPLETE
        obj.save()
    except Exception as e:
        for obj in PrimarySource.objects.filter(id=object_id):
            obj.delete()
        raise e
    finally:
        for fname in [data_file, transformation_file, materials_file]:
            if fname:
                os.remove(fname)
