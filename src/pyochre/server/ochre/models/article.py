import logging
from datetime import date
from django.db.models import ImageField, TextField, BooleanField, IntegerField, DateField, ManyToManyField
from pyochre.server.ochre.models import OchreModel, User, ResearchArtifact, ResearchProject, Course


logger = logging.getLogger(__name__)


class Article(OchreModel):
    class Meta(OchreModel.Meta):
        verbose_name_plural = "Articles"
        ordering = ["-date"]
    title = TextField()
    content = TextField(blank=True, null=True)
    thumbnail = ImageField(upload_to="article_images", null=True)
    is_active = BooleanField(default=False)
    ordering = IntegerField(default=0)
    date = DateField()
    people = ManyToManyField(User, related_name="mentioned_in")
    courses = ManyToManyField(Course, related_name="mentioned_in")
    researchartifacts = ManyToManyField(ResearchArtifact, related_name="mentioned_in")
    researchprojects = ManyToManyField(ResearchProject, related_name="mentioned_in")

    def __str__(self):
        return self.title
