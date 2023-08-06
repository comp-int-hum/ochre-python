import logging
from rest_framework.serializers import HyperlinkedIdentityField, CharField, ImageField, BooleanField, IntegerField
from pyochre.server.ochre.models import Slide
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import MonacoEditorField

logger = logging.getLogger(__name__)

    
class SlideSerializer(OchreSerializer):
    name = CharField(
        help_text="This slide's name, which also constitutes its title."
    )
    article = MonacoEditorField(
        help_text="This slide's article that goes into greater detail."
    )
    image = ImageField(
        help_text="This slide's image."
    )
    url = HyperlinkedIdentityField(
        view_name="api:slide-detail",
        lookup_field="id",
        lookup_url_kwarg="pk",
        read_only=True,
        help_text="URL of this slide."
    )
    active = BooleanField(
        default=False,
        help_text="Whether this slide is in the rotation for the site."
    )
    ordering = IntegerField(
        default=0,
        help_text="The priority of this slide in the slideshow order."
    )
    class Meta:
        model = Slide
        fields = [
            "name",
            "article",
            "image",
            "url",
            "active",
            "ordering",
            "creator_url"
        ]
