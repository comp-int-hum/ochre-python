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


logger = logging.getLogger(__name__)


widget_map = {
    OCHRE["TabularVisualization"] : TableWidget,
    OCHRE["EditorInteraction"] : MonacoEditorWidget,
    OCHRE["VegaVisualization"] : VegaWidget,
    OCHRE["AudioRecorder"] : AudioWidget,
    OCHRE["ImageRecorder"] : ImageWidget,
    OCHRE["TextEditor"] : MonacoEditorWidget
}


class MachineLearningModelInteractionField(Field):
    def __init__(self, *argv, **argd):
        super(
            MachineLearningModelInteractionField,
            self
        ).__init__(
            source="*",
            required=False,
        )
        self.field_name = "interaction_{}".format(random_token(6))
        self.style["template_pack"] = "ochre/template_pack"
                
    def to_representation(self, object, *argv, **argd):
        sig = object.signature
        in_field, out_field = None, None
        in_widget = None
        mvq_string = files("pyochre").joinpath(
            "data/model_visualization_query.sparql"
        ).read_text()
        #print(argv, argd)
        for s, p, o in sig.triples((None, OCHRE["simpleFormat"], None)):
            if s == OCHRE["Input"]:
                in_widget = input_widget_map[o]
            elif s == OCHRE["Output"]:
                out_widget = output_widget_map[o]
        tabs = {}
        self.style["endpoint_url"] = reverse("api:machinelearningmodel-apply", args=(object.id,))
        for result in sig.query("PREFIX ochre: <{}>\n".format(settings.OCHRE_NAMESPACE) + mvq_string):
            s = result["s"]
            p = result["p"]
            o = result["o"]
            tabs[s] = tabs.get(s, {})
            tabs[s][p] = tabs[s].get(p, [])
            tabs[s][p].append(o)
        tab_list = []
        for tab in tabs.values():
            props = {"endpoint" : self.style["endpoint_url"]}
            for prop, val in tab.items():
                props[prop] = props.get(prop, []) + val
            widget_type = tab[OCHRE["isA"]][0]
            widget_label = tab[OCHRE["hasDescription"]][0]
            widget_class = tab.get(OCHRE["hasLabel"], ["Unknown"])[0]
            if widget_type in widget_map:
                tab_list.append(
                    {
                        "title" : widget_label,
                        "html" : widget_map.get(widget_type)(props=props).render(
                            props[OCHRE["hasDescription"]][0],
                            object
                        )
                    }
                )
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
