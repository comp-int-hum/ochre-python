import logging
from pyochre.server.ochre.widgets import MonacoEditorWidget
from pyochre.server.ochre.fields import MonacoEditorField


logger = logging.getLogger(__name__)


class SparqlEditorField(MonacoEditorField):
    def __init__(self, *argv, **argd):
        argd["language"] = "sparql"
        retval = super(SparqlEditorField, self).__init__(*argv, **argd)
        self.style["rendering_url"] = "sparql"
        self.style["hide_label"] = True
