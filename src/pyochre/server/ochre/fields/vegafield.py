import logging
from secrets import token_hex as random_token
from rest_framework.serializers import Field
from pyochre.server.ochre import vega
from pyochre.server.ochre.decorators import ochre_cache_method


logger = logging.getLogger(__name__)


class VegaField(Field):
    
    def __init__(self, *argv, **argd):
        super(
            VegaField,
            self
        ).__init__(
            source="*",
            required=False,
            label=argd.get("label", "")
        )
        self.field_name = "interaction_{}".format(random_token(6))
        self.style["template_pack"] = "ochre/template_pack"
        self.style["base_template"] = "vega.html"
        self.vega_class = getattr(vega, str(argd["vega_class_name"]))

    #@ochre_cache_method
    def to_representation(self, value):
        return self.vega_class(
            value
        ).json
