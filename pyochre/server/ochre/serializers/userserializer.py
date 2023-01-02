import logging
from pyochre.server.ochre.fields import MonacoEditorField, ViewEditField, MarkdownEditorField
from pyochre.server.ochre.models import User
from pyochre.server.ochre.serializers import OchreSerializer


logger = logging.getLogger(__name__)


class UserSerializer(OchreSerializer):
    description = MarkdownEditorField(
        language="markdown",
        property_field="description",
        allow_blank=True,
        required=False,
        endpoint="markdown"
    )
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "homepage",
            "title",
            "photo",
            "description",
            "url",
            "id",
            "password",
            "email",
            "username",
            "created_by"
        ]
        extra_kwargs = dict(
            [
                ("password", {"write_only" : True, "required" : False}),
                ("email", {"write_only" : True, "required" : False}),
                ("username", {"write_only" : True, "required" : False}),
            ] + [
                (f, {"required" : False}) for f in [
                    "first_name",
                    "last_name",
                    "homepage",
                    "title",
                    "photo",
                    "description",
                    "url",
                    "id"
                ]
            ]
        )
        
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserSerializer, self).create(validated_data)
