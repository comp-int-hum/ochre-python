import logging
from django.db.models import ForeignKey, PositiveIntegerField, CASCADE
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from pyochre.server.ochre.models import OchreModel, AsyncMixin
from pyochre.utils import rdf_store


logger = logging.getLogger(__name__)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


class Annotation(AsyncMixin, OchreModel):
    source_type = ForeignKey(
        ContentType,
        on_delete=CASCADE,
        null=True,
        blank=True,
        editable=False
    )
    source_id = PositiveIntegerField(null=True, blank=True, editable=False)
    source_object = GenericForeignKey('source_type', 'source_id')

    @property
    def uri(self):
        return "{}{}_annotation".format(settings.OCHRE_NAMESPACE, self.id)
    
    def save(self, *argv, **argd):
        retval = super(Annotation, self).save()
        return self
