import json
import logging
from hashlib import md5
from django.conf import settings
from pairtree import PairtreeStorageFactory
import magic
from rest_framework.serializers import CharField, SerializerMethodField, Serializer


logger = logging.getLogger(__name__)


class MaterialSerializer(Serializer):
    content = CharField()
    content_type = CharField(
        allow_null=True,
        default=None
    )

    def create(self, validated_data):
        content = validated_data["content"]
        h = md5()
        h.update(content)
        mid = h.hexdigest()
        if validated_data.get("content_type"):
            content_type = validated_data["content_type"]
        else:
            content_type = magic.from_buffer(content[:2048], mime=True)
        psf = PairtreeStorageFactory()
        store = psf.get_store(
            store_dir=settings.MATERIALS_ROOT,
            uri_base=settings.OCHRE_NAMESPACE
        )
        obj = store.get_object(mid, create_if_doesnt_exist=True)
        obj.add_bytestream(
            "content",
            content
        )
        obj.add_bytestream(
            "metadata",
            json.dumps({"content_type" : content_type}).encode()
        )
        return {"material_id" : mid}

    def retrieve(self, mid):
        psf = PairtreeStorageFactory()
        store = psf.get_store(
            store_dir=settings.MATERIALS_ROOT,
            uri_base=settings.OCHRE_NAMESPACE
        )
        obj = store.get_object(mid, create_if_doesnt_exist=False)
        with obj.get_bytestream("content", streamable=True) as ifd:
            content = ifd.read()
        with obj.get_bytestream("metadata", streamable=True) as ifd:
            metadata = json.loads(ifd.read())
        return {
            "content" : content,
            "metadata" : metadata
        }
