import logging
import os.path
import json
import zipfile
from importlib.resources import files
from django.conf import settings
from django.http import HttpResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from pyochre.server.ochre.serializers import OntologySerializer
from pyochre.server.ochre.content_negotiation import OchreContentNegotiation
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
from rdflib import Graph, BNode


logger = logging.getLogger(__name__)


class OntologyViewSet(ViewSet):
    content_negotiation_class = OchreContentNegotiation
    renderer_classes = [
        #BrowsableAPIRenderer,
        #JSONRenderer,
        OchreTemplateHTMLRenderer
    ]
    template_name = "ochre/template_pack/ontology.html"
    serializer_class = OntologySerializer
    prefix = "ochre"
    schema = AutoSchema(
        tags=["ontology"],
        component_name="ontology",
        operation_id_base="ontology"
    )

    def retrieve(self, request, pk=None):
        ontology_string = files("pyochre").joinpath("data/ochre.ttl").read_text()
        g = Graph()
        g.parse(
            data="@prefix ochre: <{}> .\n{}".format(
                settings.OCHRE_NAMESPACE,
                ontology_string
            ),
            format="turtle"
        )
        terms = {}
        for s, p, o in g:
            if not isinstance(s, BNode):
                terms[s] = terms.get(s, {})
        return Response(
            {"terms" : sorted(terms.items())}
        )
