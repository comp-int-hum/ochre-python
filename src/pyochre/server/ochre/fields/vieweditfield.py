import logging
from rest_framework.serializers import Field


logger = logging.getLogger(__name__)


class ViewEditField(Field):

    def __init__(self, view, edit, *argv, **argd):
        retval = super(ViewEditField, self).__init__(*argv, **argd)
        self.view = view
        self.edit = edit
        return retval

    def to_representation(self, object, *argv, **argd):
        return self.edit.to_representation(object, *argv, **argd)

    def to_internal_value(self, *argv, **argd):
        return self.edit.to_internal_value(*argv, **argd)
