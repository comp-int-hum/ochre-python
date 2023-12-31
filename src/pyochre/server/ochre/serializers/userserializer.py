import logging
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField, ImageField
from pyochre.server.ochre.fields import MonacoEditorField
from pyochre.server.ochre.models import User
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


class UserSerializer(OchreSerializer):
    url = HyperlinkedIdentityField(
        view_name="api:user-detail",
        lookup_field="id",
        lookup_url_kwarg="pk"
    )
    biography = MonacoEditorField(
        label="Longer biography",
        language="markdown",
        property_field="biography",
        allow_blank=True,
        required=False,
    )
    research_interests = CharField(
        label="A handful of broad areas of scholarly interest",
        allow_blank=True,
        required=False,
    )
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "homepage",
            "title",
            "photo",
            "research_interests",
            "location",
            "phone",
            "id",
            "biography",
            "email"            
        ] + [x for x in OchreSerializer.Meta.fields if x != "name"]
        
    def creation_methods(self):
        return [
            {
                "title" : "Add a new user",
                "url" : "api:user-list"
            }
        ]
