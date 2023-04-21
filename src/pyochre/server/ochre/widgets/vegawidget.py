import logging
from django.forms import Media, Widget
from django.template.loader import get_template
from django.conf import settings
from secrets import token_hex as random_token
from rdflib.namespace import RDF, RDFS, Namespace
from pyochre.server.ochre import vega
from pyochre.server.ochre.decorators import ochre_cache_method


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


logger = logging.getLogger(__name__)


@ochre_cache_method
def get_spec(value, vega_class, prefix):
    return vega_class(value, prefix=prefix).json


class VegaWidget(Widget):
    template_name = "ochre/template_pack/vega.html"
    preamble = None

    def __init__(self, *argv, preamble=None, **argd):
        self.props = argd.pop("props", {})
        vega_class_name = self.props.get(OCHRE["hasLabel"])[0]#argd.get(
        #"vega_class",
        
            #str(self.props.get(OCHRE["specification"], [None])[0])
        #)[0]
        self.vega_class = getattr(vega, str(vega_class_name))
        super(VegaWidget, self).__init__(*argv, **argd)
        self.preamble = preamble
        
    def get_context(self, name, value, attrs):
        context = super(VegaWidget, self).get_context(name, value, attrs)

        context["widget"]["attrs"]["id"] = "prefix_{}".format(random_token(8))
        self.prefix = context["widget"]["attrs"]["id"]
        context["widget"]["spec_id"] = "spec_{}".format(context["widget"]["attrs"]["id"])
        context["widget"]["div_id"] = "div_{}".format(context["widget"]["attrs"]["id"])
        context["widget"]["value_id"] = "value_{}".format(context["widget"]["attrs"]["id"])
        context["widget"]["element_id"] = "element_{}".format(context["widget"]["attrs"]["id"])

        context["vega_spec"] = get_spec(value, self.vega_class, self.prefix)
        context["spec_identifier"] = "spec_{}".format(context["widget"]["attrs"]["id"])
        context["div_identifier"] = "div_{}".format(context["widget"]["attrs"]["id"])
        context["element_identifier"] = "element_{}".format(context["widget"]["attrs"]["id"])
        #print(context["vega_spec"])
        return context
