import logging
from django.db.models import ImageField, TextField, BooleanField, IntegerField, ManyToManyField, CharField
from pyochre.server.ochre.models import OchreModel, User


logger = logging.getLogger(__name__)


class Course(OchreModel):
    class Meta(OchreModel.Meta):
        verbose_name_plural = "Course"
    title = TextField()
    identifier = CharField(max_length=100, blank=True)
    description = TextField(blank=True, null=True)
    is_active = BooleanField(default=False)
    ordering = IntegerField(default=0)
    instructors = ManyToManyField(User, related_name="teaches")
