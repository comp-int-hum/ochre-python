import logging
from django.db.models import Model
from django.contrib.auth import get_user_model
from django.urls import path, reverse
from django.db.models import CharField, TextField


logger = logging.getLogger(__name__)


class AsyncMixin(Model):
    PROCESSING = "PR"
    ERROR = "ER"
    COMPLETE = "CO"
    STATE_CHOICES = [
        (PROCESSING, "processing"),
        (ERROR, "error"),
        (COMPLETE, "complete")
    ]
    state = CharField(
        max_length=2,
        choices=STATE_CHOICES,
        default=PROCESSING,
        editable=False
    )
    message = TextField(null=True, editable=False)
    task_id = CharField(max_length=200, null=True, editable=False)
    
    class Meta:
        abstract = True
