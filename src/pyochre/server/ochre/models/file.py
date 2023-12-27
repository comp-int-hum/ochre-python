import logging
from datetime import date
from django.db.models import UniqueConstraint
from django.db.models import FileField
from pyochre.server.ochre.models import OchreModel, User


logger = logging.getLogger(__name__)


class File(OchreModel):
    class Meta(OchreModel.Meta):
        verbose_name_plural = "Files"
        ordering = ["-created_at"]
        constraints = [
            UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_name",
                fields=["name"]
            )
        ]

    item = FileField(upload_to="user_uploads", null=False)

    def __str__(self):
        return self.name
