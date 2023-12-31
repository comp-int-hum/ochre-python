import logging
from django import template


logger = logging.getLogger(__name__)


register = template.Library()


@register.simple_tag(takes_context=True)
def join(
        context,        
        prefix,
        suffix
):
    return "{}_{}".format(str(prefix), str(suffix))
