import logging
from secrets import token_hex as random_token
from django.urls import reverse
from django.conf import settings
from rest_framework.serializers import Field, HyperlinkedIdentityField, SerializerMethodField
from pyochre.server.ochre.fields import MonacoEditorField, ObjectDetectionField, AudioTranscriptionField, VegaField
from pyochre.server.ochre.models import PrimarySource
from pyochre.server.ochre.widgets import VegaWidget
from pyochre.server.ochre import vega
from rdflib import URIRef
from rdflib.namespace import RDF, RDFS, Namespace


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


logger = logging.getLogger(__name__)


class DataField(HyperlinkedIdentityField):

    def __init__(self, *argv, **argd):
        super(
            DataField,
            self
        ).__init__(
            view_name=argd["view_name"],
            #vega_class_name="PrimarySourceDataGraph"
            #source="*",
            #required=False,
        )
        self.view_name = argd["view_name"]
        self.field_name = "data_{}".format(random_token(6))
        #self.style["template_pack"] = "ochre/template_pack"
        #self.style["base_template"] = "vega.html"
        #self.style["widget"] = VegaWidget(props={"vega_class" : "PrimarySourceDomainGraph"})
        #self.style["vega_class"] = "PrimarySourceDomainGraph"
                
    #def to_representation(self, object, *argv, **argd):
        #sig = object.domain
    #    return super(DomainField, self).to_representation(object, *argv, **argd)

    #def to_internal_value(self, data):
    #    return data
