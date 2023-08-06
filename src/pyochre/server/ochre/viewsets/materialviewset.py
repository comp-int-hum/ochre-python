import logging
import os.path
import json
import zipfile
from django.conf import settings
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from pairtree import PairtreeStorageFactory
from pyochre.server.ochre.serializers import MaterialSerializer
from pyochre.server.ochre.content_negotiation import OchreContentNegotiation
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
from pyochre.server.ochre.autoschemas import OchreAutoSchema


logger = logging.getLogger(__name__)


class MaterialViewSet(GenericViewSet):
    content_negotiation_class = OchreContentNegotiation
    renderer_classes = [
        BrowsableAPIRenderer,
        JSONRenderer,
        OchreTemplateHTMLRenderer
    ]
    serializer_class = MaterialSerializer
    schema = OchreAutoSchema(
        tags=["material"],
        component_name="material",
        operation_id_base="material"
    )

    #def list(self, request, pk=None):
    #    return Response({"next" : None, "results" : []})
    
    def destroy(self, request, pk=None):
        """
        Destroy (delete) a material file.
        """
        psf = PairtreeStorageFactory()
        store = psf.get_store(
            store_dir=os.path.join(
                settings.MATERIALS_ROOT,
                self.prefix
            ),
            uri_base=settings.OCHRE_NAMESPACE
        )
        obj = store.get_object(pk, create_if_doesnt_exist=False)
        for fname in obj.list_parts():
            obj.del_file(fname)
        return Response(status=200)

    def retrieve(self, request, pk=None):
        """
        Retrieve a material file.
        """
        ser = MaterialSerializer()
        m = ser.retrieve(pk)
        return Response(m)
    
