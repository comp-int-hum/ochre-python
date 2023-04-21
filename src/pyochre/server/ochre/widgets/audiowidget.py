import logging
from django.urls import reverse
from django.forms import Media, Widget
from secrets import token_hex as random_token
from django.utils.html import html_safe


logger = logging.getLogger(__name__)


class AudioWidget(Widget):
    template_name = "ochre/template_pack/audio.html"
    id = None
    
    def __init__(self, *args, **kwargs):
        #self.object = object
        self.language = None #kwargs.get("language", "javascript")
        #self.default_value = kwargs.get("default_value", "")
        self.field_name = kwargs.get("name", "content")
        self.endpoint = kwargs.get("props", {}).get("endpoint", None)
        default_attrs = {}
        #    "language" : kwargs.get("language", "javascript"),
        #    "field_name" : kwargs.get("name", "content"),
        #    "endpoint" : kwargs.get("endpoint", None),
        #}
        #default_attrs.update(kwargs.get("attrs", {}))
        super(AudioWidget, self).__init__(default_attrs)

    def get_context(self, name, value, attrs):
        context = super(
            AudioWidget,
            self
        ).get_context(name, value, attrs)
        context["css"] = self.media._css["all"]
        context["js"] = self.media._js
        context["widget"]["attrs"]["id"] = "prefix_{}".format(
            random_token(8)
        )
        context["widget"]["value_id"] = "value_{}".format(
            context["widget"]["attrs"]["id"]
        )
        context["widget"]["output_id"] = "output_{}".format(
            context["widget"]["attrs"]["id"]
        )
        # context["widget"]["value"] = (
        #     context["widget"]["value"] if context["widget"].get(
        #         "value",
        #         None
        #     ) else self.default_value
        # )
        rid = "prefix_{}".format(random_token(8))
        context["field"] = {
            "name" : self.field_name,
            "value" : value
        }
        context["style"] = {
            "base_template" : "editor.html",
            "css" : self.media._css["all"],
            "js" : self.media._js,
            "id" : rid,
            "value_id" : "value_{}".format(rid),
            "output_id" : "output_{}".format(rid),
            "language" : self.language,
            "endpoint" : self.language,
            "template_pack" : "ochre/template_pack",
            "editable" : True,
            "field_name" : "monaco_{}".format(random_token(6)),
            "endpoint_url" : self.endpoint
        }
        return context

    def value_from_datadict(self, data, files, name):
        return super(
            MonacoEditorWidget,
            self
        ).value_from_datadict(data, files, name)
    
    @property
    def media(self):
        return Media(
            css = {
                'all': (
                ),
            },
            js = (
            )
        )
