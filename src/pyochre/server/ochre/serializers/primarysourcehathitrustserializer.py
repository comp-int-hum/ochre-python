import os.path
import logging
import io
import zipfile
import re
import csv
import tempfile
from rest_framework.serializers import HyperlinkedIdentityField, FileField, BooleanField
from django.conf import settings
from rdflib import Namespace
from pyochre.server.ochre.models import PrimarySource, Query, Annotation
from pyochre.server.ochre.serializers import OchreSerializer
from rdflib import Graph, BNode, URIRef, Literal, Dataset
from rdflib.namespace import RDF, RDFS, XSD, Namespace
from pyochre.server.ochre.models import PrimarySource, User
from pairtree import PairtreeStorageFactory
from pyochre.utils import rdf_store
from pyochre.primary_sources import create_domain


logger = logging.getLogger(__name__)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


@shared_task
def primarysource_from_hathitrust_collection(
        primarysource_id,
        collection_string,
):
    ps = PrimarySource.objects.get(id=primarysource_id)
    try:
        psf = PairtreeStorageFactory()
        g = Graph(base="http://test/")
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
            #g.add((text, OCHRE["hasMaterialId"], Literal(row["htid"])))
            g.add((text, OCHRE["hasValue"], Literal(full_content)))
            if "author" in row:
                g.add((author, OCHRE["hasLabel"], Literal(row["author"])))            
                g.add((text, OCHRE["hasAuthor"], author))
                g.add((author, OCHRE["isA"], OCHRE["Author"]))
            if "imprint" in row:
                g.add((publisher, OCHRE["isA"], OCHRE["Publisher"]))
                g.add((text, OCHRE["hasPublisher"], publisher))
                g.add((publisher, OCHRE["hasLabel"], Literal(row["imprint"])))                
            if "pub_place" in row:
                g.add((text, OCHRE["hasLocation"], Literal(row["pub_place"])))
            if "rights_date_used" in row:
                if row["rights_date_used"].isdigit():
                    g.add((text, OCHRE["hasDate"], Literal(row["rights_date_used"], datatype=XSD.integer)))
            if "lang" in row:
                g.add((text, OCHRE["inLanguage"], Literal(row["lang"])))
            if "title" in row:
                g.add((text, OCHRE["hasLabel"], Literal(row["title"])))
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


class PrimarySourceHathiTrustSerializer(OchreSerializer):    

    collection_file = FileField(
        write_only=True,
        help_text="A collection CSV file downloaded from the HathiTrust interface"
    )
    force = BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
        default=False,
        help_text="Overwrite any existing primary source of the same name and creator"
    )
    
    class Meta:
        model = PrimarySource
        fields = [
            "name",
            "force",
            "collection_file",
            "id",
            "url",
        ]

    def create(self, validated_data):
        obj = PrimarySource(
            name=validated_data["name"],
            created_by=validated_data["created_by"],
            state=PrimarySource.PROCESSING,
            message="This primary source is being processed..."
        )
        obj.save()
        primarysource_from_hathitrust_collection.delay(
            obj.id,
            validated_data["collection_file"].read().decode("utf-8")
        )
        return obj

    def update(self, instance, validated_data):        
        super(
            PrimarySourceSerializer,
            self
        ).update(
            instance,
            validated_data
        )
        instance.save(**validated_data)
        return instance
    
