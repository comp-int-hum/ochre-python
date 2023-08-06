import os.path
import logging
import re
import tempfile
from rest_framework.serializers import HyperlinkedIdentityField, FileField, BooleanField, ChoiceField
from django.conf import settings
from rdflib import Namespace, Graph, Dataset
from lxml.etree import XML, XSLT, parse, TreeBuilder, tostring, XSLTExtension, fromstring
from pyochre.server.ochre.models import PrimarySource, Query, Annotation
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.utils import meta_open, rdf_store
from pyochre.primary_sources import TsvParser, CsvParser, JsonParser, create_domain, enrich_uris, NoHeaderTsvParser, NoHeaderCsvParser, XmlParser, JsonLineParser, parsers


logger = logging.getLogger(__name__)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


def file_type(fname):
    _, ext = os.path.splitext(re.sub(r"\.(gz|bz2)$", "", fname))
    return ext[1:]


@shared_task
def primarysource_from_xsl_transformation(
        object_id,
        data_file,
        data_file_type,
        transformation_file,
        split_data
):
    try:
        obj = PrimarySource.objects.get(id=object_id)
        
        logger.info("Load the XML-to-RDF transformation rules")
        with meta_open(transformation_file, "rt") as ifd:
            tr_str = re.sub(
                r"xmlns:ochre\s*=\s*\"urn:ochre:\"",
                "xmlns:ochre=\"{}\"".format(settings.OCHRE_NAMESPACE),
                ifd.read()
            )
            transform = XSLT(fromstring(tr_str.encode()))

        logger.info("Instantiating the necessary X-to-XML parser")
        parser = parsers[data_file_type]()

        logger.info("Creating XML from the original data")
        with meta_open(data_file, "rt") as ifd:
            for xml in parser(ifd, split=split_data):
                logger.info("Creating RDF from XML")
                tr = transform(xml, ochre_namespace="'{}'".format(settings.OCHRE_NAMESPACE))
                logger.info("Loading the RDF")
                resp = obj.add(tostring(tr))
                
        obj.infer_domain()
        obj.state = obj.COMPLETE
        obj.save()
    except Exception as e:
        for obj in PrimarySource.objects.filter(id=object_id):
            obj.delete()
        raise e
    finally:
        for fname in [data_file, transformation_file]:
            if fname:
                os.remove(fname)


class PrimarySourceXslTransformationSerializer(OchreSerializer):    

    data_file = FileField(
        write_only=True,
        help_text="Data in some supported non-RDF format (e.g. XML, JSON, CSV)"
    )

    data_file_type = ChoiceField(
        write_only=True,
        help_text="Format of data file",
        choices=list(parsers.keys())
    )
    
    transformation_file = FileField(
        write_only=True,
        required=True,
        help_text="XSL file describing the transformation of the data into RDF"
    )
    force = BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
        default=False,
        help_text="Overwrite any existing primary source of the same name and creator"
    )

    split_data = BooleanField(
        write_only=True,
        default=False,
        required=False,
        allow_null=True,
        help_text="Split data files to emulate streaming (may lead to incorrect RDF for some formats/transformations)"
    )
    
    
    class Meta:
        model = PrimarySource
        slug = "Using an XSL transformation"
        fields = [
            "name",
            "force",
            "data_file",
            "data_file_type",
            "transformation_file",
            "split_data",
            #"id",
            #"url",
            "created_by"
        ]

    def create(self, validated_data):
        if validated_data.get("force", False):
            for existing in PrimarySource.objects.filter(
                    name=validated_data["name"],
                    created_by=validated_data["created_by"]
            ):
                existing.delete()
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
        #if validated_data.get("materials_file", False):
        #    _, mf_name = tempfile.mkstemp(
        #        suffix=os.path.basename(validated_data["materials_file"].name),
        #        dir=settings.TEMP_ROOT
        #    )
        #else:
        #    mf_name = None
        for stream, fname in [
                (validated_data.get("data_file"), d_name),
                (validated_data.get("transformation_file"), tr_name),
                #(validated_data.get("materials_file"), mf_name)
        ]:
            if fname:
                with open(fname, "wb") as ofd:
                    ofd.write(stream.read())
        
        obj.task_id = primarysource_from_xsl_transformation.delay(
            obj.id,
            d_name,
            validated_data["data_file_type"],
            tr_name,
            #mf_name,
            validated_data.get("split_data", False)
        )
        obj.save()
        return obj

    
