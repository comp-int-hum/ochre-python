import logging
import re
import os.path
import json
import zipfile
from importlib.resources import files
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from pyochre.server.ochre.serializers import OntologySerializer, OntologyInteractiveSerializer
from pyochre.server.ochre.content_negotiation import OchreContentNegotiation
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
from rdflib import Graph, BNode
from pyochre.server.ochre.autoschemas import OchreAutoSchema
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.utils import ochrequery as OQ
import requests
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import OWL, RDFS


logger = logging.getLogger(__name__)


class OntologyViewSet(OchreViewSet):
    list_template_name = "ochre/template_pack/ontology.html"
    #renderer_classes = [
    #    OchreTemplateHTMLRenderer,
    #    BrowsableAPIRenderer,
    #    JSONRenderer
    #]


    schema = OchreAutoSchema(
        tags=["ontology"],
        component_name="ontology",
        operation_id_base="ontology"
    )
    model = None
    def get_serializer_class(self):
        if isinstance(self.request.accepted_renderer, OchreTemplateHTMLRenderer):
            return OntologyInteractiveSerializer        
        else:
            return OntologySerializer

    #def get_template_names(self):
    #    return ["ochre/template_pack/ontology.html"]
        
    def list(self, request, pk=None):
        """
        Retrieve the current OCHRE ontology.
        """
        resp = requests.get(
            "{}/ochre/data".format(settings.JENA_URL),
            params={"graph" : settings.ONTOLOGY_URI},
            headers={"Accept" : "text/turtle", "charset" : "utf-8"}
        )
        ser = self.get_serializer_class()(resp.content) #data={"graph" : resp.content})
        #if ser.is_valid():
        return Response(ser.data)

        #else:
        #    return Response(
        #        ser.errors,
        #        status=status.HTTP_400_BAD_REQUEST
        #    )
            
        # classes = {}
        # for binding in g.query(
        #         OQ(
        #             """
        #             SELECT ?class ?wde ?desc
        #             WHERE {
        #               ?class ochre:equivalentClass ?wde .
        #               OPTIONAL { ?wde rdfs:comment ?desc . }
        #             }                    
        #             """
        #         )
        # ):
        #     name = re.sub(
        #         "^{}".format(settings.OCHRE_NAMESPACE),
        #         "",
        #         str(binding["class"])
        #     )
        #     classes[name] = binding.asdict() #{"url" : binding["wde"], "description" : binding.get("desc")}

        # properties = {}            
        # for binding in g.query(
        #         OQ(
        #             """
        #             SELECT ?prop ?wdp ?desc
        #             WHERE {
        #               ?prop ochre:equivalentProperty ?wdp .
        #               OPTIONAL { ?wdp rdfs:comment ?desc . }
        #             }                    
        #             """
        #         )
        # ):
        #     name = re.sub(
        #         "^{}".format(settings.OCHRE_NAMESPACE),
        #         "",
        #         str(binding["prop"])
        #     )
        #     properties[name] = binding.asdict()
            
        #return Response(
        #    {"triples" : json.loads(g.serialize(format="json-ld"))},
            #{"classes" : classes, "properties" : properties},
            #template_name="ochre/template_pack/ontology.html"

        #)

    @action(detail=False, methods=["POST"])
    def regenerate(self, request, pk=None):
        """
        Regenerate OCHRE ontology based on the state of the ochre.ttl file.
        """
        OCHRE = Namespace(settings.OCHRE_NAMESPACE)
        sig_string = files("pyochre").joinpath("data/ochre.ttl").read_text()

        ns = Namespace(settings.OCHRE_NAMESPACE)
        g = Graph()
        g.parse(
            data="@prefix ochre: <{}> .\n".format(settings.OCHRE_NAMESPACE) + sig_string,
            format="turtle"
        )
        from wikidata.client import Client
        client = Client()
        
        to_add = {}
        wikidata_descriptions = {}
        wikidata_parent_descriptions = {}
        for s, p, o in g:
            if p in [OCHRE["equivalentClass"], OCHRE["equivalentProperty"]] and "wikidata" in str(o):
                name = str(o).split("/")[-1]
                entity = client.get(name, load=True)
                if entity.data:
                    wikidata_descriptions[o] = Literal(entity.description)
        for s, p, o in g:
            if p in [OCHRE["subClassOf"], OCHRE["subPropertyOf"]] and "wikidata" in str(o):
                name = str(o).split("/")[-1]
                entity = client.get(name, load=True)
                if entity.data:
                    wikidata_parent_descriptions[o] = Literal(entity.description)
                    
        for k, v in wikidata_descriptions.items():
            g.add((k, RDFS["comment"], v))
        for k, v in wikidata_parent_descriptions.items():
            g.add((k, RDFS["comment"], v))            
        resp = requests.put(
            "{}/ochre/data".format(settings.JENA_URL),
            params={"graph" : settings.ONTOLOGY_URI},
            data=g.serialize(format="text/turtle"),
            headers={"Content-type" : "text/turtle"}
        )
        return Response()
