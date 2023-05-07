import logging
import re
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import serializers


logger = logging.getLogger(__name__)


class OchreAutoSchema(AutoSchema):
    def __init__(
            self,
            tags=None,
            operation_id_base=None,
            component_name=None,
            response_serializer=None
    ):
        super(
            OchreAutoSchema,
            self
        ).__init__(
            tags,
            operation_id_base,
            component_name
        )
        self.response_serializer = response_serializer

    def get_response_serializer(self, path, method):
        if self.response_serializer:
            return self.response_serializer()
        else:
            return self.get_serializer(path, method)
        
    def get_default_basename(self, viewset):
        return super(OchreAutoSchema, self).get_default_basename(self, viewset)

    def get_component_name(self, serializer):
        component_name = serializer.__class__.__name__
        pattern = re.compile("serializer", re.IGNORECASE)
        self.component_name = pattern.sub("", component_name)
        return self.component_name
    
    def get_components(self, path, method):
        return super(OchreAutoSchema, self).get_components(path, method)

    def get_operation(self, path, method):
        return super(OchreAutoSchema, self).get_operation(path, method)

    def get_operation_id(self, path, method):
        return super(OchreAutoSchema, self).get_operation_id(path, method)

    def get_description(self, path, method):
        return super(OchreAutoSchema, self).get_description(path, method)

    def map_field(self, field):
        retval = super(OchreAutoSchema, self).map_field(field)
        if isinstance(field, serializers.HyperlinkedRelatedField):
            retval["format"] = "object"
            if field.queryset:
                retval["discriminator"] = re.sub(
                    r"{}\.".format(field.queryset.model._meta.app_label),
                    "",
                    field.queryset.model._meta.label
                )

        return retval
