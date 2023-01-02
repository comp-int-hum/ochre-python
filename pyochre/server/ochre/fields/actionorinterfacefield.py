import logging
from rest_framework.serializers import HyperlinkedIdentityField


logger = logging.getLogger(__name__)


class ActionOrInterfaceField(HyperlinkedIdentityField):
    
    def __init__(self, interface_field, *argv, **argd):
        self.nested_parent_field = argd.pop("nested_parent_field", False)
        title = argd.pop("title", None)
        retval = super(ActionOrInterfaceField, self).__init__(*argv, **argd)
        self.style["title"] = title
        self.title = title
        self.interface_field = interface_field
        self.read_only = argd.get("read_only", False)        
        return retval

    def to_representation(self, object, *argv, **argd):
        self.interface_field.style["object"] = object
        if self.nested_parent_field:
            self.interface_field.style["parent_id"] = getattr(object, self.nested_parent_field).id
        return super(ActionOrInterfaceField, self).to_representation(object, *argv, **argd)
