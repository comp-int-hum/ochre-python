import logging
from django.db.models import Model, JSONField


logger = logging.getLogger(__name__)


class MetadataMixin(Model):
    metadata = JSONField(
        default=dict,
        editable=False,
    )

    class Meta:
        abstract = True

        
