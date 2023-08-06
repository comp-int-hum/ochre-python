import logging
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField
from pyochre.server.ochre.fields import MonacoEditorField
from pyochre.server.ochre.models import User
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


class UserInteractiveSerializer(OchreSerializer):
    description = MonacoEditorField(
        language="markdown",
        property_field="description",
        allow_blank=True,
        required=False,
        #endpoint="markdown"
    )
    biography = MonacoEditorField(
        language="markdown",
        property_field="description",
        allow_blank=True,
        required=False,
        #endpoint="markdown"
    )
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "title",
            "homepage",
            "photo",
            "description",
            "biography",
            "email",
        ]
        # extra_kwargs = dict(
        #     [
        #         ("password", {"write_only" : True, "required" : False}),
        #         ("email", {"write_only" : True, "required" : False}),
        #         ("username", {"read_only" : True, "required" : False}),
        #     ] + [
        #         (f, {"required" : False}) for f in [
        #             "first_name",
        #             "last_name",
        #             "homepage",
        #             "title",
        #             "photo",
        #             "description",
        #             "url",
        #             "id"
        #         ]
        #     ]
        # )
