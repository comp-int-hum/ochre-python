import logging
from django.db.models import ImageField, TextField
from pyochre.server.ochre.models import OchreModel


logger = logging.getLogger(__name__)


class Slide(OchreModel):
    article = TextField(blank=True, null=True)
    image = ImageField(blank=True, upload_to="slides")
    
    class Meta:
        verbose_name_plural = "Slides"
