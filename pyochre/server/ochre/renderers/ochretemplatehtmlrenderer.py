import logging
from rest_framework.renderers import TemplateHTMLRenderer


logger = logging.getLogger(__name__)


class OchreTemplateHTMLRenderer(TemplateHTMLRenderer):
    format = "ochre"
    
    def get_template_context(self, data, renderer_context):
        context = super(
            OchreTemplateHTMLRenderer,
            self
        ).get_template_context(
            data,
            renderer_context
        )
        context = {
            "items" : context
        } if isinstance(context, list) else context
        for k, v in renderer_context.items():
            if not context.get(k):
                context[k] = v
            else:
                logger.debug(
                    "Not replacing %s with %s for context item %s",
                    context.get(k),
                    v,
                    k
                )
        return context
