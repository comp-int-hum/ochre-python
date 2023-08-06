import logging
from importlib.resources import files
from django.conf import settings
from secrets import token_hex as random_token
from django.urls import reverse
from rest_framework.serializers import Field, HyperlinkedIdentityField
from pyochre.server.ochre.fields import MonacoEditorField, ObjectDetectionField, AudioTranscriptionField
from pyochre.server.ochre.models import MachineLearningModel
from pyochre.server.ochre.widgets import MonacoEditorWidget, ImageWidget, AudioWidget, TableWidget, VegaWidget
import pyochre.server.ochre.widgets as widgets
from pyochre.server.ochre import vega
from rdflib import URIRef
from rdflib.namespace import RDF, RDFS, Namespace


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


logger = logging.getLogger(__name__)


class InteractionField(Field):
    
    def __init__(self, *argv, parameters, description, widget_class, **argd):
        super(
            InteractionField,
            self
        ).__init__(
            source="*",
            required=False,
            label=description
        )
        self.field_name = "interaction_{}".format(random_token(6))
        self.style["template_pack"] = "ochre/template_pack"
        self.widget_class = getattr(widgets, widget_class)
        self.style["base_template"] = self.widget_class.base_template
        
    def to_representation(self, value):
        #self.widget_class(
        return "tesfsat"
