import logging
from importlib.resources import files
from django.conf import settings
from secrets import token_hex as random_token
from django.urls import reverse
from rest_framework.serializers import Field, HyperlinkedIdentityField
from pyochre.server.ochre.fields import MonacoEditorField, ObjectDetectionField, AudioTranscriptionField
from pyochre.server.ochre.models import MachineLearningModel
from pyochre.server.ochre.widgets import MonacoEditorWidget, ImageWidget, AudioWidget, TableWidget, VegaWidget
from pyochre.server.ochre import vega
from rdflib import URIRef
from rdflib.namespace import RDF, RDFS, Namespace


OCHRE = Namespace(settings.OCHRE_NAMESPACE)
#WDE = Namespace("http://www.wikidata.org/entity/")
#WDP = Namespace("http://www.wikidata.org/prop/direct/")


logger = logging.getLogger(__name__)


#input_widget_map = {
#    WDE["Q26987229"] : AudioWidget,
#    WDE["Q86920"] : MonacoEditorWidget,
#    WDE["Q860625"] : ImageWidget
#}


#output_widget_map = {
#    WDE["Q26987229"] : AudioWidget,
#    WDE["Q86920"] : MonacoEditorWidget,
#    WDE["Q860625"] : ImageWidget
#}


widget_map = {
    OCHRE["TabularVisualization"] : TableWidget,
    OCHRE["EditorInteraction"] : MonacoEditorWidget,
    OCHRE["VegaVisualization"] : VegaWidget
}


class AnnotationInteractionField(Field):
    def __init__(self, *argv, **argd):
        super(
            AnnotationInteractionField,
            self
        ).__init__(
            source="*",
            required=False,
        )
        self.field_name = "interaction_{}".format(random_token(6))
        self.style["template_pack"] = "ochre/template_pack"
                
    def to_representation(self, object, *argv, **argd):
        #anns = object.annotations
        #data = object.primarysource.data
        #for s, p, o in object.annotations:
        #    data.add((s, p, o))
        tab_list = [
            {
                "title" : "Temporal evolution",
                "html" : VegaWidget(
                    props={
                        OCHRE["hasLabel"] : ["TemporalEvolution"]
                    }
                ).render(
                    "test",
                    object
                )
            }
        #             "html" : widget_map.get(widget_type)(props=props).render(
        #                 props[OCHRE["hasDescription"]][0],
        #                 object
        #             )
        ]
        if len(tab_list) == 0:
            self.style["base_template"] = "interaction.html"
            self.style["rendered_widget"] = {"html" : "There does not seem to be anything to show about this model."}
        elif len(tab_list) == 1:
            self.style["base_template"] = "interaction.html"
            self.style["rendered_widget"] = tab_list[0]
        else:
            self.style["base_template"] = "tabs_interaction.html"
            self.style["tabs"] = tab_list
        self.style["hide_label"] = True
        self.style["interactive"] = True
        self.style["object"] = object
        return str(object)

    def to_internal_value(self, data):
        return {}
