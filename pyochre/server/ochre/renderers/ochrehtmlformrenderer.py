import logging
from rest_framework.renderers import HTMLFormRenderer
from rest_framework.utils.serializer_helpers import BoundField
from pyochre.server.ochre.fields import ActionOrInterfaceField


logger = logging.getLogger(__name__)


class OchreHTMLFormRenderer(HTMLFormRenderer):
    
    def __init__(self, *argv, **argd):
        return super(OchreHTMLFormRenderer, self).__init__(*argv, **argd)

    def render(
            self,
            data,
            accepted_media_type=None,
            renderer_context=None
    ):
        for style_field_name in ["mode", "tab_view", "uid", "index"]:
            if style_field_name in renderer_context:
                renderer_context["style"][style_field_name] = \
                    renderer_context[style_field_name]
        self.uid = renderer_context["uid"]
        self.request = renderer_context.get("request", None)
        return super(OchreHTMLFormRenderer, self).render(
            data,
            accepted_media_type=accepted_media_type,
            renderer_context=renderer_context
        )
    
    def render_field(self, field, parent_style, *argv, **argd):
        field.context["request"] = self.request
        if isinstance(field._field, ActionOrInterfaceField):
            # if GET then pull value from object, else empty
            inter = field._field.interface_field
            inter.context["request"] = self.request
            if hasattr(inter, "get_actual_field"):
                inter = inter.get_actual_field(parent_style)
            field = BoundField(inter, inter.get_default_value(), [])
        return super(OchreHTMLFormRenderer, self).render_field(
            field,
            parent_style,
            *argv,
            **argd
        )
