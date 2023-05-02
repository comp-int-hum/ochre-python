import os.path
import logging
import tempfile
from rest_framework.serializers import HyperlinkedIdentityField, FileField, BooleanField
from django.conf import settings
from pyochre.server.ochre.models import PrimarySource, Query, Annotation
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.tasks import expand_primarysource


logger = logging.getLogger(__name__)


class PrimarySourceSerializer(OchreSerializer):    

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
            message="This primary source is still being processed..."
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
        
        obj.task_id = expand_primarysource.delay(
            obj.id,
            d_name,
            tr_name,
            mf_name,
            validated_data.get("split_data", False)
        )
        obj.save()
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
    
