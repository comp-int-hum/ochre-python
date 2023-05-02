from rest_framework.schemas.openapi import SchemaGenerator
from django.conf import settings

class OchreSchemaGenerator(SchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        schema["info"]["namespace"] = settings.OCHRE_NAMESPACE
        return schema
