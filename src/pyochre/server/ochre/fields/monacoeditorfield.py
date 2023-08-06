import logging
from secrets import token_hex as random_token
from django.forms import Media
from rest_framework.serializers import CharField, Field


logger = logging.getLogger(__name__)


class MonacoEditorField(Field):

    def __init__(self, *argv, **argd):
        super(
            MonacoEditorField,
            self
        ).__init__(
            required=False,
            #source="*",
            label=argd.get("label", ""),
            help_text=argd.get("help_text"),
            style=argd.get("style", {})
        )
        self.field_name = "interaction_{}".format(random_token(6))
        self.style["template_pack"] = "ochre/template_pack"
        self.style["base_template"] = "editor.html"
        self.style["endpoint"] = str(argd["endpoint"]) if "endpoint" in argd else None
        self.style["language"] = argd.get("language", "")
        #self.style["freeform"] = argd.get("freeform", False)
        #self.help_text = argd.get("help_text")
        #self.style["hide_label"] = argd.get("hide_label", "")
        
    def to_representation(self, value):
        return value
        #if self.style["freeform"]:
        #    return ""
        #else:
        #    return value
        #return value.id
        #{
        #   "contents" : value.,
        #   "instance" : value
       #}

    def to_internal_value(self, data):
        return data
