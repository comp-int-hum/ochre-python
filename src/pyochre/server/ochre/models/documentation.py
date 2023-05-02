import logging
from django.db.models import CharField, TextField, ForeignKey, PositiveIntegerField, CASCADE, Index
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import markdown
from pyochre.server.ochre.models import OchreModel


logger = logging.getLogger(__name__)


class Documentation(OchreModel):
    class Meta(OchreModel.Meta):
        indexes = [
            Index(fields=["referent_type", "referent_id"]),
        ]

    content = TextField(blank=True, null=True)
    view_name = CharField(
        null=True,
        max_length=200,
        editable=False
    )
    referent_type = ForeignKey(
        ContentType,
        on_delete=CASCADE,
        null=True,
        blank=True,
        editable=False
    )
    referent_id = PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
    )
    referent_object = GenericForeignKey(
        'referent_type',
        'referent_id',
    )

    def render(self):
        return markdown.markdown(self.content)
