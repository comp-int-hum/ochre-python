import logging
from django.forms import Media, Widget
from django.template.loader import get_template
from secrets import token_hex as random_token


logger = logging.getLogger(__name__)


class VegaWidget(Widget):
    template_name = "ochre/template_pack/vega.html"
    preamble = None

    def __init__(self, vega_class, *argv, preamble=None, **argd):
        super(VegaWidget, self).__init__(*argv, **argd)
        self.vega_class = vega_class
        self.preamble = preamble
        
    def get_context(self, name, value, attrs):
        context = super(VegaWidget, self).get_context(name, value, attrs)

        context["widget"]["attrs"]["id"] = "prefix_{}".format(random_token(8))
        self.prefix = context["widget"]["attrs"]["id"]
        context["widget"]["spec_id"] = "spec_{}".format(context["widget"]["attrs"]["id"])
        context["widget"]["div_id"] = "div_{}".format(context["widget"]["attrs"]["id"])
        context["widget"]["element_id"] = "element_{}".format(context["widget"]["attrs"]["id"])

        context["vega_spec"] = self.vega_class(value, prefix=self.prefix).json
        context["spec_identifier"] = "spec_{}".format(context["widget"]["attrs"]["id"])
        context["div_identifier"] = "div_{}".format(context["widget"]["attrs"]["id"])
        context["element_identifier"] = "element_{}".format(context["widget"]["attrs"]["id"])
        return context
