import logging
from django.db.models.fields.related import ForeignKey
from rest_framework.serializers import ModelSerializer, HiddenField, HyperlinkedIdentityField, CurrentUserDefault, CharField, HyperlinkedRelatedField, ImageField, Serializer, FileField, BooleanField, IntegerField
from pyochre.server.ochre.models import Slide
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)

    
class SlideUploadSerializer(OchreSerializer):
    name = CharField()
    title = CharField()
    article_file = FileField(required=False, allow_null=True)
    image_file = ImageField()
    active = BooleanField(required=False, allow_null=True, default=False)
    ordering = IntegerField(
        required=False,
        allow_null=True,
        default=0
    )
    
    class Meta:
        model = Slide
        fields = [
            "name",
            "title",
            "article_file",
            "image_file",
            "active",
            "ordering",
            "created_by"
        ]
