import logging
from secrets import token_hex as random_token
from rest_framework.serializers import Field


logger = logging.getLogger(__name__)


class VegaField(Field):
    visual_only = True
    def __init__(self, vega_class, *argv, **argd):
        property_field = argd.pop("property_field", None)
        self.property_field_args = argd.pop("property_field_args", {})
        self.title = argd.pop("title", "")
        retval = super(VegaField, self).__init__(*argv, **argd)
        self.vega_class = vega_class
        self.style["property_field"] = property_field
        self.style["base_template"] = "vega.html"
        self.style["template_pack"] = "ochre/template_pack"
        self.style["id"] = "{}".format(random_token(8))
        self.style["value_id"] = "value_{}".format(self.style["id"])
        self.style["spec_id"] = "spec_{}".format(self.style["id"])
        self.style["div_id"] = "div_{}".format(self.style["id"])
        self.style["editable"] = True
        self.field_name = "vega_{}".format(random_token(6))
        return retval

    def get_attribute(self, object, **argd):
        return getattr(object, self.style["property_field"])(**self.property_field_args)

    def get_default_value(self):
        retval = self.vega_class(
            getattr(self.style["object"], self.style["property_field"])(**self.property_field_args),
            self.style["div_id"]
        ).json
        return retval
    
    def to_representation(self, object, *argv, **argd):
        retval = self.vega_class(
            object,
            self.style["div_id"]
        ).json
        return retval
