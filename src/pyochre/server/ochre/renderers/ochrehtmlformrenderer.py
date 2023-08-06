import logging
from django.template import engines, loader

from rest_framework.renderers import HTMLFormRenderer
from rest_framework.utils.serializer_helpers import BoundField
from rest_framework.serializers import Field

logger = logging.getLogger(__name__)


class OchreHTMLFormRenderer(HTMLFormRenderer):

    def __init__(self, *argv, **argd):
        super(OchreHTMLFormRenderer, self).__init__(*argv, **argd)

    def render(
            self,
            data,
            accepted_media_type=None,
            renderer_context=None
    ):
        self.uid = renderer_context["uid"]
        self.request = renderer_context.get("request", None)
        retval = super(OchreHTMLFormRenderer, self).render(
            data,
            accepted_media_type=accepted_media_type,
            renderer_context=renderer_context,
        )
        return retval
    
    def render_field(self, field, parent_style, *argv, **argd):
        field.context["request"] = self.request
        retval = super(OchreHTMLFormRenderer, self).render_field(
            field,
            parent_style,
            *argv,
            **argd
        )
        return retval
