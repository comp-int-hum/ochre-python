import logging
from django.forms import Textarea, Widget


logger = logging.getLogger(__name__)


class TableWidget(Widget):
    def __init__(self, *argv, **argd):
        super(TableWidget, self).__init__(*argv, **argd)

    def get_context(self, name, value, attrs):
        context = super(TableWidget, self).get_context(name, value, attrs)
        return context
