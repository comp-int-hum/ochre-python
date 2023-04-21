import logging
from django.forms import Textarea, Media
from secrets import token_hex as random_token
from django.utils.html import html_safe


logger = logging.getLogger(__name__)


class MonacoEditorWidget(Textarea):
    template_name = "ochre/template_pack/editor.html"
    id = None
    
    def __init__(self, *args, **kwargs):
        self.language = kwargs.get("language", "plain")
        self.field_name = kwargs.get("name", "content")
        self.endpoint = kwargs.get("props", {}).get("endpoint", None)
        default_attrs = {}
        super(MonacoEditorWidget, self).__init__(default_attrs)

    def get_context(self, name, value, attrs):
        context = super(
            MonacoEditorWidget,
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
        rid = "prefix_{}".format(random_token(8))
        context["field"] = {
            "name" : self.field_name,
            "value" : "" #value, the string
        }
        context["style"] = {
            "base_template" : "editor.html",
            "css" : self.media._css["all"],
            "js" : self.media._js,
            "id" : rid,
            "value_id" : "value_{}".format(rid),
            "output_id" : "output_{}".format(rid),
            "language" : self.language,
            "endpoint" : self.endpoint,
            "template_pack" : "ochre/template_pack",
            "editable" : True,
            "field_name" : "monaco_{}".format(random_token(6)),
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
