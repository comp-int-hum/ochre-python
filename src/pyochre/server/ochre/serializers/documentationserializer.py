import logging
from collections import OrderedDict, defaultdict
from rest_framework.serializers import ModelSerializer, BaseSerializer, HyperlinkedModelSerializer, HiddenField, HyperlinkedIdentityField, ReadOnlyField, CurrentUserDefault, HyperlinkedRelatedField, PrimaryKeyRelatedField, CharField, IntegerField, Serializer, CreateOnlyDefault
from django.contrib.contenttypes.models import ContentType
from pyochre.server.ochre.fields import MarkdownEditorField
from pyochre.server.ochre.models import Documentation


logger = logging.getLogger(__name__)


class DocumentationSerializer(ModelSerializer):
    content = MarkdownEditorField(
        language="markdown",
        property_field="content",
        allow_blank=True,
        required=False,
        endpoint="markdown"
    )

    view_name = CharField(
        style={"hidden" : True}
    )
        
    referent_id = IntegerField(
        required=False,
        allow_null=True,
        style={"hidden" : True},
    )
    
    referent_type = PrimaryKeyRelatedField(
        queryset=ContentType.objects,
        allow_null=True,
        style={"hidden" : True}
    )

    name = CharField(
        style={"hidden" : True}
    )
    
    created_by = HiddenField(
        default=CurrentUserDefault()
    )
    
    class Meta:
        model = Documentation        
        fields = [
            "content",
            "name",
            "view_name",
            "referent_type",
            "referent_id",
            "created_by",
            "id"
        ]

