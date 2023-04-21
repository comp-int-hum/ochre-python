import logging
from wiki.editors.base import BaseEditor
from pyochre.server.ochre.widgets import MonacoEditorWidget


logger = logging.getLogger(__name__)


class WikiMarkdownField(BaseEditor):
    editor_id = "markitup"

    def get_admin_widget(self, instance=None):
        return MonacoEditorWidget(language="markdown", endpoint="markdown")

    def get_widget(self, instance=None):
        return MonacoEditorWidget(language="markdown", endpoint="markdown")

    class AdminMedia:
        css = {
        }
        js = (
        )

    class Media:
        css = {
            "all": (
            )
        }
        js = (
        )
