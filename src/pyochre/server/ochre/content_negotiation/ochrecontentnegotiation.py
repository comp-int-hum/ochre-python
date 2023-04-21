import logging
from rest_framework.negotiation import DefaultContentNegotiation


logger = logging.getLogger(__name__)


class OchreContentNegotiation(DefaultContentNegotiation):

    def select_renderer(
            self,
            request,
            renderers,
            format_suffix
    ):
        if "include=true" in request.headers.get(
                "Accept",
                ""
        ) or request.headers.get("include"):
            return (renderers[-1], renderers[-1].media_type)
        else:
            return super(
                OchreContentNegotiation,
                self
            ).select_renderer(request, renderers, format_suffix)
