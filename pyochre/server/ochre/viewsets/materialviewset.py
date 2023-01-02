import logging
import os.path
import json
import zipfile
from django.conf import settings
from django.http import HttpResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from pairtree import PairtreeStorageFactory
from pyochre.server.ochre.serializers import MaterialSerializer
from pyochre.server.ochre.content_negotiation import OchreContentNegotiation
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer


logger = logging.getLogger(__name__)


class MaterialViewSet(ViewSet):
    content_negotiation_class = OchreContentNegotiation
    renderer_classes = [
        BrowsableAPIRenderer,
        JSONRenderer,
        OchreTemplateHTMLRenderer
    ]
    serializer_class = MaterialSerializer
    prefix = "ochre"
    schema = AutoSchema(
        tags=["material"],
        component_name="material",
        operation_id_base="material"
    )
    accordion_header_template_name = None

    def create(self, request, pk=None):
        content = request.data["file"]
        content_type = request.data["content_type"]
        uid = request.data["uid"]
        psf = PairtreeStorageFactory()
        store = psf.get_store(
            store_dir=os.path.join(
                settings.MATERIALS_ROOT,
                self.prefix
            ),
            uri_base=settings.OCHRE_NAMESPACE
        )
        obj = store.get_object(uid, create_if_doesnt_exist=True)
        obj.add_bytestream(
            "content",
            content
        )
        obj.add_bytestream(
            "metadata",
            json.dumps({"content_type" : content_type}).encode()
        )
        return Response(status=201)
    
    def destroy(self, request, pk=None):
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
        psf = PairtreeStorageFactory()
        store = psf.get_store(
            store_dir=os.path.join(
                settings.MATERIALS_ROOT,
                self.prefix
            ),
            uri_base=settings.OCHRE_NAMESPACE
        )
        obj = store.get_object(pk, create_if_doesnt_exist=False)
        fnames = obj.list_parts()
        metadata = {}
        files = {}
        for fname in fnames:
            if fname == "metadata":
                files["metadata"] = fname
            elif fname == "content":
                files["content"] = fname
            elif fname.endswith(".mets.xml"):
                files["hathitrust_metadata"] = fname
            elif fname.endswith(".zip"):
                files["hathitrust_content"] = fname
            else:
                raise Exception("Unrecognized stream name: {}".format(fname))
        if "metadata" in files and "content" in files:
            metadata = json.loads(
                obj.get_bytestream(
                    files["metadata"],
                    streamable=True
                ).read()
            )
            with obj.get_bytestream(files["content"], streamable=True) as ifd:
                content = ifd.read()
        elif "hathitrust_metadata" in files and "hathitrust_content" in files:
            metadata = {
                "content_type" : "text/plain"
            }
            zf = o.get_bytestream(
                os.path.join(
                    part,
                    files["hathitrust_content"]
                ),
                streamable=True
            )
            document_pages = []
            with zipfile.ZipFile(zf, "r") as zifd:
                for page in zifd.namelist():
                    document_pages.append(
                        zifd.read(page).decode("utf-8")
                    )
            content = "\n".join(document_pages)
        else:
            raise Exception(
                """
                Material '{}' doesn't have content/metadata or
                hathitrust_content/hathitrust_metadata files
                """
            )
        return HttpResponse(
            content,
            content_type=metadata.get("content_type", "unknown")
        )
