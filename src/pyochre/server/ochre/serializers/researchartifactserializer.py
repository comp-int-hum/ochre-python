import logging
from django.db.models.fields.related import ForeignKey
from pyochre.server.ochre.models import ResearchArtifact
from pyochre.server.ochre.fields import MarkdownEditorField
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


class ResearchArtifactSerializer(OchreSerializer):
    #description = MarkdownEditorField(
    #    language="markdown",
    #    property_field="description",
    #    allow_blank=True,
    #    required=False,
    #    endpoint="markdown"
    #)
    
    class Meta:
        model = ResearchArtifact
        fields = [
            f.name for f in ResearchArtifact._meta.fields if not isinstance(f, ForeignKey)
        ] + [
            "url",
            "created_by"
        ]
        #view_fields = ["description"]
        edit_fields = [
            f.name for f in ResearchArtifact._meta.fields if not isinstance(f, ForeignKey)
        ] + [
            "url",
            "created_by"
        ]
        create_fields = [
            f.name for f in ResearchArtifact._meta.fields if not isinstance(f, ForeignKey)
        ] + [
            "url",
            "created_by"
        ]
        extra_kwargs = dict([(f, {"required" : False}) for f in create_fields])
