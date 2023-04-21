import logging
from secrets import token_hex as random_token
from django.urls import reverse
from django.conf import settings
from rest_framework.serializers import Field, HyperlinkedIdentityField
from pyochre.server.ochre.fields import MonacoEditorField, ObjectDetectionField, AudioTranscriptionField
from pyochre.server.ochre.models import PrimarySource
from pyochre.server.ochre.widgets import VegaWidget
from pyochre.server.ochre import vega
from rdflib import URIRef
from rdflib.namespace import RDF, RDFS, Namespace


OCHRE = Namespace(settings.OCHRE_NAMESPACE)
#WDE = Namespace("http://www.wikidata.org/entity/")
#WDP = Namespace("http://www.wikidata.org/prop/direct/")


logger = logging.getLogger(__name__)


class PrimarySourceInteractionField(Field):

    def __init__(self, *argv, **argd):
        super(
            PrimarySourceInteractionField,
            self
        ).__init__(
            source="*",
            required=False,
        )
        self.field_name = "interaction_{}".format(random_token(6))
        self.style["template_pack"] = "ochre/template_pack"
                
    def to_representation(self, object, *argv, **argd):
        sig = object.domain
        tabs = []
        tabs.append(
            {
                "title" : "Domain",
                "html" : VegaWidget(
                    props={
                        #OCHRE["specification"] : ["PrimarySourceDomainGraph"],
                        OCHRE["hasLabel"] : ["PrimarySourceDomainGraph"],
                    }
                ).render("Domain", object)
            }
        )            
        if len(tabs) == 0:
            self.style["base_template"] = "interaction.html"
            self.style["rendered_widget"] = {"html" : "There does not seem to be anything to show about this primary source."}
        elif len(tabs) == 1:
            self.style["base_template"] = "interaction.html"
            self.style["rendered_widget"] = tabs[0]
        else:
            self.style["base_template"] = "tabs_interaction.html"
            self.style["tabs"] = tabs
        self.style["hide_label"] = True
        self.style["interactive"] = True
        self.style["object"] = object
        return str(object)
    
    def to_internal_value(self, data):
        return {}
