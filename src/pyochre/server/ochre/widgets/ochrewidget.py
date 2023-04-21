import logging
from django.forms import Widget, MultiWidget
from secrets import token_hex as random_token


logger = logging.getLogger(__name__)


class OchreWidget(Widget):
    pass
