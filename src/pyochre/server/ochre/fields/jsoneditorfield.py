import logging
from pyochre.server.ochre.widgets import MonacoEditorWidget
from pyochre.server.ochre.fields import MonacoEditorField


logger = logging.getLogger(__name__)


class JsonEditorField(MonacoEditorField):
    def __init__(self, *argv, **argd):
        argd["language"] = "json"
        retval = super(JsonEditorField, self).__init__(*argv, **argd)
        self.style["hide_label"] = True
