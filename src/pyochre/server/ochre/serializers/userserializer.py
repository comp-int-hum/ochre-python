import logging
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField
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
        label="Longer biography (may use Markdown)",
        language="markdown",
        property_field="biography",
        allow_blank=True,
        required=False,
    )
    research_interests = CharField(
        label="A handful of broad areas of scholarly interest",
        #language="text",
        #property_field="description",
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
            "url",
            "id",
            "biography",
            "email",
            "is_active",
        ]
        # extra_kwargs = dict(
        #     [
        #         #("password", {"write_only" : True, "required" : False}),
        #         ("email", {"read_only" : True, "required" : False}),
        #         ("username", {"read_only" : True, "required" : False}),
        #     ] + [
        #         (f, {"required" : False}) for f in [
        #             "first_name",
        #             "last_name",
        #             "homepage",
        #             "title",
        #             "photo",
        #             "research_interests",
        #             "phone",
        #             "location"
        #             #"description",
        #             "url",
        #             "id"
        #         ]
        #     ]
        # )
        
    def creation_methods(self):
        return [
            {
                "title" : "Add a new user",
                "url" : "api:user-list"
            }
        ]
    
    # def create(self, validated_data, message=None):
    #     if "force" in validated_data:
    #         if validated_data["force"] == True:
    #             for existing in self.Meta.model.objects.filter(
    #                     email=validated_data["email"],
    #                     created_by=validated_data["created_by"]
    #             ):
    #                 existing.delete()
    #         validated_data.pop("force")
    #     obj = super(OchreSerializer, self).create(validated_data)
    #     if message:
    #         obj.message = message
    #     obj.save()
    #     return obj

        
    #def create(self, validated_data):
    #    validated_data['password'] = make_password(validated_data.get('password'))
    #    return super(UserSerializer, self).create(validated_data)
