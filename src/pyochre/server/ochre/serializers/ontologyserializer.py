import logging
from rest_framework.serializers import CharField, SerializerMethodField, Serializer


logger = logging.getLogger(__name__)


class OntologySerializer(Serializer):
    
    def __init__(self, *argv, **argd):
        retval = super(Serializer, self).__init__(*argv, **argd)
        return retval

    #def to_representation(self, instance):
    #    return None

    #def to_internal_value(self, data):
    #    return None
