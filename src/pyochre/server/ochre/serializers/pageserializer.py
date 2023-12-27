import logging
from rest_framework.serializers import HyperlinkedIdentityField, CharField, ImageField, BooleanField, IntegerField
from pyochre.server.ochre.models import Page
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import MonacoEditorField

logger = logging.getLogger(__name__)

    
class PageSerializer(OchreSerializer):
    name = CharField(
        help_text="This banner's name, which will also be how it is related to its corresponding page, so perhaps one of 'index', 'About', 'People', 'Research', or 'Teaching'."
    )
    banner_overlay = MonacoEditorField(
        help_text="The content that will appear over the righthand side of the banner."
    )
    url = HyperlinkedIdentityField(
        view_name="api:page-detail",
        lookup_field="id",
        lookup_url_kwarg="pk",
        read_only=True,
        help_text="URL of this page."
    )
    description = MonacoEditorField(
        help_text="The description that will appear over underneath the banner."
    )
    class Meta:
        model = Page
        fields = [            
            f.name for f in Page._meta.fields
        ] + OchreSerializer.Meta.fields
