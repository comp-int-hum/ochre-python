import logging
from django.db.models import ImageField, TextField, BooleanField, IntegerField
from pyochre.server.ochre.models import OchreModel


logger = logging.getLogger(__name__)


class Slide(OchreModel):
    class Meta(OchreModel.Meta):
        verbose_name_plural = "Slides"
    title = TextField()
    article = TextField(blank=True, null=True)
    image = ImageField(upload_to="slides")
    active = BooleanField(default=False)
    ordering = IntegerField()
