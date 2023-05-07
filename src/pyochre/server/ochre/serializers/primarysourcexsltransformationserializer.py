import os.path
import logging
import re
import tempfile
from rest_framework.serializers import HyperlinkedIdentityField, FileField, BooleanField
from django.conf import settings
from rdflib import Namespace, Graph, Dataset
from lxml.etree import XML, XSLT, parse, TreeBuilder, tostring, XSLTExtension
from pyochre.server.ochre.models import PrimarySource, Query, Annotation
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.utils import meta_open, rdf_store
from pyochre.primary_sources import TsvParser, CsvParser, JsonParser, create_domain, enrich_uris, NoHeaderTsvParser, NoHeaderCsvParser, XmlParser


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
def primarysource_from_xsl_transformation(
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
                tr = transform(xml) #, ochre_namespace=settings.OCHRE_NAMESPACE)
                

                logger.info("Loading the RDF and skolemizing it")
                g = Graph(base="http://test/")
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


class PrimarySourceXslTransformationSerializer(OchreSerializer):    

    data_file = FileField(
        write_only=True,
        help_text="Data in some supported non-RDF format (e.g. XML, JSON, CSV)"
    )

    transformation_file = FileField(
        write_only=True,
        required=True,
        help_text="XSL file describing the transformation of the data into RDF"
    )

    materials_file = FileField(
        write_only=True,
        help_text="Data in some supported non-RDF format (e.g. XML, JSON, CSV)",
        required=False,
        allow_null=True
    )

    split_data = BooleanField(
        write_only=True,
        default=True,
        required=False,
        allow_null=True,
        help_text="Split data files to emulate streaming (may lead to incorrect RDF for some formats/transformations)"
    )
    
    domain_url = HyperlinkedIdentityField(
        view_name="api:primarysource-domain"
    )
    
    clear_url = HyperlinkedIdentityField(
        view_name="api:primarysource-clear"
    )
    
    query_url = HyperlinkedIdentityField(
        view_name="api:primarysource-query"
    )
    
    update_url = HyperlinkedIdentityField(
        view_name="api:primarysource-sparqlupdate"
    )    
    
    class Meta:
        model = PrimarySource
        fields = [
            "name",
            "data_file",
            "transformation_file",
            "materials_file",
            "split_data",
            "domain_url",
            "creator",
            "id",
            "url",
            "clear_url",
            "query_url",
            "update_url"
        ]

    def create(self, validated_data):
        logger.info("Creating new primarysource")
        obj = PrimarySource(
            name=validated_data["name"],
            created_by=validated_data["created_by"],
            state=PrimarySource.PROCESSING,
            message="This primary source is being processed..."
        )
        obj.save()
        _, d_name = tempfile.mkstemp(
            suffix=os.path.basename(validated_data["data_file"].name),
            dir=settings.TEMP_ROOT
        )
        _, tr_name = tempfile.mkstemp(
            suffix=os.path.basename(validated_data["transformation_file"].name),
            dir=settings.TEMP_ROOT
        )
        if validated_data.get("materials_file", False):
            _, mf_name = tempfile.mkstemp(
                suffix=os.path.basename(validated_data["materials_file"].name),
                dir=settings.TEMP_ROOT
            )
        else:
            mf_name = None
        for stream, fname in [
                (validated_data.get("data_file"), d_name),
                (validated_data.get("transformation_file"), tr_name),
                (validated_data.get("materials_file"), mf_name)
        ]:
            if fname:
                with open(fname, "wb") as ofd:
                    ofd.write(stream.read())
        
        obj.task_id = primarysource_from_xsl_transformation.delay(
            obj.id,
            d_name,
            tr_name,
            mf_name,
            validated_data.get("split_data", False)
        )
        obj.save()
        return obj

    
