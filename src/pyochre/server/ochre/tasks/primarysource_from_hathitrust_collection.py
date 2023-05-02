import io
import time
import zipfile
import random
import pickle
import json
from urllib.parse import urlencode
import csv
import gzip
import os.path
import logging
import re
import os
import tarfile
import tempfile
import os.path
from importlib.resources import files
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from rdflib import Graph, BNode, URIRef, Literal, Dataset
from rdflib.namespace import RDF, RDFS, XSD, Namespace
from pyochre.server.ochre.models import PrimarySource, User
from pairtree import PairtreeStorageFactory
from pyochre.utils import rdf_store
from pyochre.primary_sources import create_domain


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


logger = logging.getLogger(__name__)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


@shared_task
def primarysource_from_hathitrust_collection(
        collection_string,
        name,
        created_by_id
):
    ps = PrimarySource(
        name=name,
        created_by=User.objects.get(id=created_by_id),
        state=PrimarySource.PROCESSING,
        message="This primary source is still being processed..."
    )
    ps.save()
    psf = PairtreeStorageFactory()
    g = Graph(base="http://test/")
    try:
        c = csv.DictReader(io.StringIO(collection_string), delimiter="\t")
        for row in c:
            toks = row["htid"].split(".")
            subcollection = toks[0]
            ident = ".".join(toks[1:])
            store = psf.get_store(
                store_dir=os.path.join(
                    settings.HATHITRUST_ROOT,
                    subcollection
                ),
                uri_base=settings.OCHRE_NAMESPACE
            )
            try:
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
                                    txt = re.sub(r"\-\s*?\n\s*", "", txt)
                                    full_content.append(txt)
                                    
            full_content = "\n".join(full_content)
            # author lang title rights_date_used pub_place imprint
            text = BNode()
            author = BNode()
            publisher = BNode()
            publication_place = BNode()
            g.add((text, OCHRE["isA"], OCHRE["Text"]))
            g.add((text, OCHRE["hasValue"], Literal(full_content)))
            g.add((text, OCHRE["hasAuthor"], author))
            g.add((author, OCHRE["isA"], OCHRE["Author"]))
            g.add((publisher, OCHRE["isA"], OCHRE["Publisher"]))
            g.add((text, OCHRE["hasPublisher"], publisher))
            g.add((text, OCHRE["hasLocation"], Literal(row["pub_place"])))
            if row["rights_date_used"].isdigit():
                g.add((text, OCHRE["hasDate"], Literal(row["rights_date_used"], datatype=XSD.integer)))
            g.add((text, OCHRE["inLanguage"], Literal(row["lang"])))
            g.add((text, OCHRE["hasLabel"], Literal(row["title"])))
            g.add((author, OCHRE["hasLabel"], Literal(row["author"])))
            g.add((publisher, OCHRE["hasLabel"], Literal(row["imprint"])))
        g = g.skolemize()
        store = rdf_store(settings=settings)
        dataset = Dataset(store=store, default_graph_base=OCHRE)
        logger.info("Getting the named graph corresponding to the primary source")
        ng = dataset.graph(
            OCHRE["{}_data".format(ps.id)]
        )
        for tr in g:
            ng.add(tr)
        ng.commit()
        dg = dataset.graph(
           OCHRE["{}_domain".format(ps.id)]
        )
        for s, p, o in create_domain(ps):
           dg.add((s, p, o))
        store.commit()
        ps.state = ps.COMPLETE
        ps.save()
    except Exception as e:
        ps.delete()
        raise e
    finally:
        pass
