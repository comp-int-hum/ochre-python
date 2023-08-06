import logging
from django.conf import settings
from django.db.models import FileField, CharField, ImageField, TextField, URLField, PositiveIntegerField, BooleanField, IntegerField, ManyToManyField
from pyochre.server.ochre.models import OchreModel, User


logger = logging.getLogger(__name__)


class ResearchProject(OchreModel):
    class Meta(OchreModel.Meta):
        pass

    title = TextField()
    abstract = TextField(blank=True, null=True)
    content = TextField(blank=True, null=True)
    thumbnail = ImageField(upload_to="researchproject_images", null=True)
    is_active = BooleanField(default=False)
    ordering = IntegerField(default=0)
    researchers = ManyToManyField(User, related_name="participates_in")
    
    def __str__(self):
        return self.title

