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


class DomainField(VegaField):

    def __init__(self, *argv, **argd):
        super(
            DomainField,
            self
        ).__init__(
            vega_class_name="PrimarySourceDomainGraph"
        )
        self.view_name = argd["view_name"]
        self.field_name = "domain_{}".format(random_token(6))
