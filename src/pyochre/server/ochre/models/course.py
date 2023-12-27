import logging
from django.db.models import ImageField, TextField, BooleanField, IntegerField, ManyToManyField, CharField
from pyochre.server.ochre.models import OchreModel, User


logger = logging.getLogger(__name__)


class Course(OchreModel):
    class Meta(OchreModel.Meta):
        verbose_name_plural = "Course"
    title = TextField()
    identifier = CharField(max_length=100, blank=True)
    description = TextField(blank=True, null=False, default="")
    instructors = ManyToManyField(User, related_name="teaches")

    def __str__(self):
        return self.title
