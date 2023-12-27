import logging
from django.db.models import ImageField, TextField, CharField, BooleanField
from pyochre.server.ochre.models import OchreModel


logger = logging.getLogger(__name__)


class Page(OchreModel):
    class Meta(OchreModel.Meta):
        verbose_name_plural = "Pages"
    banner_overlay = TextField(blank=True, null=False, default="")    
    banner_image = ImageField(upload_to="banners", null=True)
    description = TextField(blank=True, null=False, default="")
    dynamic_content_view = CharField(blank=True, null=True, max_length=100)
    is_top_level = BooleanField(default=False)
    is_index = BooleanField(default=False)
    
    def __str__(self):
        return self.name
