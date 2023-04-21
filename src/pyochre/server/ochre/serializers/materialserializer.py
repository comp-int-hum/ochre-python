import logging
from rest_framework.serializers import CharField, SerializerMethodField, Serializer


logger = logging.getLogger(__name__)


class MaterialSerializer(Serializer):
    prefix = CharField()
    key = CharField()
    content = SerializerMethodField()
    metadata = SerializerMethodField()
    
    def __init__(self, *argv, **argd):
        retval = super(Serializer, self).__init__(*argv, **argd)
        return retval

    def create(self, validated_data):
        pass

    def get_content(self):
        pass
