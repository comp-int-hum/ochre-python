import logging
from django.db.models.fields.related import ForeignKey
from pyochre.server.ochre.models import Slide
from pyochre.server.ochre.fields import MarkdownEditorField
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)

    
class SlideSerializer(OchreSerializer):
    article = MarkdownEditorField(
        language="markdown",
        property_field="article",
        allow_blank=True,
        required=False,
        endpoint="markdown"
    )
    
    class Meta:
        model = Slide
        fields = [
            f.name for f in Slide._meta.fields if not isinstance(f, ForeignKey)
        ] + [
            "url",
            "created_by"
        ]
