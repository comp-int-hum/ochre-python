import re
import os.path
import logging
from importlib.resources import files
from django.conf import settings
from rdflib import Graph, Namespace, URIRef, Literal
from rest_framework.serializers import CharField, SerializerMethodField, Serializer, JSONField


logger = logging.getLogger(__name__)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


class OntologyInteractiveSerializer(Serializer):

    def __init__(self, *argv, **argd):
        retval = super(Serializer, self).__init__(*argv, **argd)
        return retval

    def to_representation(self, instance):
        dq = files("pyochre").joinpath("data/domain_lexicon_query.sparql").read_text()
        tq = files("pyochre").joinpath("data/term_query.sparql").read_text()
        g = Graph()
        g.parse(data=instance, format="turtle")
        retval = {"domains" : {}}
        classes = {}
        properties = {}
        for binding in g.query(tq):
            s = os.path.basename(str(binding["s"]))
            ext = str(binding["external"])
            rt = os.path.basename(str(binding["rt"]))
            prop = rt in ["subPropertyOf", "equivalentProperty"]
            desc = binding["description"].value if binding.get("description") else ""
            if prop:
                properties[s] = properties.get(s, {"description" : desc, "external" : ext})
                properties[s][binding["p"]] = binding["o"]
            else:
                classes[s] = classes.get(s, {"description" : desc, "external" : ext})
                classes[s][binding["p"]] = binding["o"]
        for binding in g.query(dq):
            label = binding["label"].value
            desc = binding["desc"].value
            part = os.path.basename(binding["part"])
            retval["domains"][label] = retval["domains"].get(
                label,
                {"classes" : {}, "properties" : {}, "description" : desc}
            )
            if part in properties:
                
                retval["domains"][label]["properties"][part] = retval["domains"][label]["properties"][part] = properties[part] #.get(part, {})
                #retval["domains"][label]["properties"][part][
            elif part in classes:
                retval["domains"][label]["classes"][part] = retval["domains"][label]["classes"][part] = classes[part]
                #retval["domains"][label]["classes"][part] = {}
        return retval
