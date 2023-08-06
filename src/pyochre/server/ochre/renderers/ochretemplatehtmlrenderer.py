import logging
from rest_framework.renderers import TemplateHTMLRenderer


logger = logging.getLogger(__name__)


class OchreTemplateHTMLRenderer(TemplateHTMLRenderer):
    format = "ochre"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return super(OchreTemplateHTMLRenderer, self).render(
            data,
            accepted_media_type,
            renderer_context
        )
    
    def get_template_context(self, data, renderer_context):
        context = super(
            OchreTemplateHTMLRenderer,
            self
        ).get_template_context(
            data,
            renderer_context
        )
        if not isinstance(context, dict):
            context = {"items" : context}
        context["serializer"] = renderer_context.get("serializer")
        return context
