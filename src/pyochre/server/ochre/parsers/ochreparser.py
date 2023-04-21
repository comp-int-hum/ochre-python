import logging
from rest_framework.parsers import BaseParser


logger = logging.getLogger(__name__)


class OchreParser(BaseParser):
    """
    Plain text parser.
    """
    media_type = '*/*'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        """
        return stream.read()
