import logging
from rest_framework.serializers import HyperlinkedIdentityField, CharField, ImageField, BooleanField, IntegerField
from pyochre.server.ochre.models import Page
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import MonacoEditorField

logger = logging.getLogger(__name__)

    
class PageSerializer(OchreSerializer):
    name = CharField(
        help_text="This page name, perhaps one of 'index', 'About', 'People', 'Research', or 'Teaching' ('index' is special, designating the initial landing page, not an item on the navigation bar)."
    )
    banner_overlay = MonacoEditorField(
        help_text="Content that will appear over the righthand side of the banner.",
        language="markdown"
    )
    banner_image = ImageField(
        help_text="Banner image, should have approx. 4-to-1 ration of width-to-height.",
        required=False,
        allow_null=True
    )
    url = HyperlinkedIdentityField(
        view_name="api:page-detail",
        lookup_field="id",
        lookup_url_kwarg="pk",
        read_only=True,
        help_text="URL of this page."
    )
    description = MonacoEditorField(
        help_text="Description that will appear underneath the banner.",
        language="markdown"
    )
    class Meta:
        model = Page
        fields = [            
            f.name for f in Page._meta.fields
        ] + OchreSerializer.Meta.fields
