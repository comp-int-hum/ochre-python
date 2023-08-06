import logging
from django.conf import settings
from django.db.models import FileField, CharField, ImageField, TextField, URLField, PositiveIntegerField, ManyToManyField, BooleanField, IntegerField
from pyochre.server.ochre.models import OchreModel, User, ResearchProject


logger = logging.getLogger(__name__)


class ResearchArtifact(OchreModel):
    class Meta(OchreModel.Meta):
        ordering = ["-year", "-month"]

    ARTICLE = "article"
    BOOK = "book"
    BOOKLET = "booklet"
    CONFERENCE = "conference"
    INBOOK = "inbook"
    INCOLLECTION = "incollection"
    INPROCEEDINGS = "inproceedings"
    MANUAL = "manual"
    MASTERSTHESIS = "mastersthesis"
    MISC = "misc"
    PHDTHESIS = "phdthesis"
    PROCEEDINGS = "proceedings"
    TECHREPORT = "techreport"
    UNPUBLISHED = "unpublished"    
    TYPE_CHOICES = [
        (ARTICLE, "Article"),
        (BOOK, "Book"),
        (BOOKLET, "Booklet"),
        (CONFERENCE, "Conference"),
        (INBOOK, "Contribution to book"),
        (INCOLLECTION, "Contribution to collection"),
        (INPROCEEDINGS, "Contribution to conference or workshop"),
        (MANUAL, "Technical documentation"),
        (MASTERSTHESIS, "Masters thesis"),
        (MISC, "Miscellaneous"),
        (PHDTHESIS, "PhD thesis"),
        (PROCEEDINGS, "Conference or workshop proceedings"),
        (TECHREPORT, "Technical report"),
        (UNPUBLISHED, "Unpublished")
    ]    
    type = CharField(max_length=100, choices=TYPE_CHOICES, default=ARTICLE)
    title = TextField(null=False)
    author = TextField(null=True)
    year = PositiveIntegerField(null=True)
    doi = CharField(max_length=1000, null=True)
    pages = CharField(max_length=1000, null=True)
    howpublished = CharField(max_length=1000, null=True)
    chapter = CharField(max_length=1000, null=True)
    organization = CharField(max_length=1000, null=True)
    booktitle = CharField(max_length=1000, null=True)
    school = CharField(max_length=1000, null=True)
    institution = CharField(max_length=1000, null=True)
    publisher = CharField(max_length=1000, null=True)
    address = CharField(max_length=1000, null=True)
    journal = CharField(max_length=1000, null=True)
    volume = CharField(max_length=1000, null=True)
    number = CharField(max_length=1000, null=True)
    series = CharField(max_length=1000, null=True)
    month = CharField(max_length=1000, null=True)
    note = CharField(max_length=1000, null=True)
    key = CharField(max_length=1000, null=True)
    editor = CharField(max_length=1000, null=True)
    edition = CharField(max_length=1000, null=True)
    biburl = URLField(max_length=1000, null=True)
    slides = FileField(upload_to="researchartifact/slides", null=True)
    document = FileField(upload_to="researchartifact/documents", null=True)
    appendix = FileField(upload_to="researchartifact/appendices", null=True)
    image = ImageField(upload_to="researchartifact/images", null=True)
    recording = FileField(upload_to="researchartifact/recordings", null=True)
    description = TextField(blank=True, null=True)
    abstract = TextField(blank=True, null=True)
    ordering = IntegerField(default=0)
    is_active = BooleanField(default=False)
    contributors = ManyToManyField(User, related_name="contributed_to")
    related_to = ManyToManyField(ResearchProject, related_name="produced")
    def __str__(self):
        return self.title

