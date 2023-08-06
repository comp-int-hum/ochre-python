import logging
from django.db.models.fields.related import ForeignKey
from rest_framework.serializers import ModelSerializer, HiddenField, HyperlinkedIdentityField, CurrentUserDefault, CharField, HyperlinkedRelatedField, ImageField, Serializer
from pyochre.server.ochre.models import Slide
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import MonacoEditorField


logger = logging.getLogger(__name__)

    
class SlideInteractiveSerializer(OchreSerializer):
    name = CharField()
    image = ImageField()
    article = MonacoEditorField()
    class Meta:
        model = Slide
        fields = [
            "name",
            "image",
            "article"
        ]
