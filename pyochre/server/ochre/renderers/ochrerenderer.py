import logging
from rest_framework.renderers import BaseRenderer


logger = logging.getLogger(__name__)


class OchreRenderer(BaseRenderer):
    format = "*"
    media_type = "*/*"
    def render(
            self,
            data,
            accepted_media_type=None,
            renderer_context=None
    ):
        return data
