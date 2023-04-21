import logging
from secrets import token_hex as random_token
from django.forms import Media
from rest_framework.serializers import CharField
from pyochre.server.ochre.widgets import MonacoEditorWidget


logger = logging.getLogger(__name__)


class MonacoEditorField(CharField):
    def __init__(self, *argv, **argd):
        property_field = argd.pop("property_field", None)        
        detail_endpoint = argd.pop("detail_endpoint", False)
        endpoint = argd.pop("endpoint", False)
        language = argd.pop("language", "")
        self.nested_parent_field = argd.pop("nested_parent_field", None)
        retval = super(MonacoEditorField, self).__init__() #*argv, **argd)
        self.style["property_field"] = property_field
        self.style["base_template"] = "editor.html"
        self.style["css"] = self.media._css["all"]
        self.style["js"] = self.media._js
        self.style["id"] = "prefix_{}".format(random_token(8))
        self.style["value_id"] = "value_{}".format(self.style["id"])
        self.style["output_id"] = "output_{}".format(self.style["id"])
        self.style["language"] = language
        self.style["detail_endpoint"] = detail_endpoint
        self.style["endpoint"] = endpoint
        self.style["template_pack"] = "ochre/template_pack"
        self.style["editable"] = False
        self.field_name = "monaco_{}".format(random_token(6))
        return retval
    
    def get_default_value(self):
        return ""

    @property
    def media(self):
        return Media(
            css = {
                'all': (
                    "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.34.0-dev.20220627/min/vs/editor/editor.main.min.css",
                ),
            },
            js = (
                "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.34.0-dev.20220625/min/vs/loader.min.js",
            )
        )
