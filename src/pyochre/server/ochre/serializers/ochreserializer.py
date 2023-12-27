import logging
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer, HiddenField, CurrentUserDefault, SerializerMethodField, ReadOnlyField, BooleanField, CharField, IntegerField


logger = logging.getLogger(__name__)


class OchreSerializer(ModelSerializer):
    created_by = HiddenField(
        default=CurrentUserDefault()
    )
    creator_url = SerializerMethodField(
        help_text="URL of the user that created this object."
    )
    permissions_url = SerializerMethodField(
        help_text="URL of the user that created this object."
    )
    
    force = BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
        default=False,
        help_text="Overwrite any existing object of the same type, name, and creator."
    )
    name = CharField()
    ordering = IntegerField(
        default=0,
        help_text="The ordering priority of this object when displayed in a list."
    )    
    def get_creator_url(self, instance):
        if instance and instance.created_by:
            return reverse(
                "api:user-detail",
                args=(instance.created_by.id,),
                request=self.context["request"]
            )
        else:
            return ""        

    def get_permissions_url(self, instance):
        if instance:
            return instance.get_permissions_url()
        else:
            return ""

    def partial_update(self, *argv, **argd):
        return self.update(*argv, **argd)

    def creation_methods(self):
        return []

    def create(self, validated_data, message=None):
        if "force" in validated_data:
            if validated_data["force"] == True:
                for existing in self.Meta.model.objects.filter(
                        name=validated_data["name"],
                        created_by=validated_data["created_by"]
                ):
                    existing.delete()
            validated_data.pop("force")
        obj = super(OchreSerializer, self).create(validated_data)
        if message:
            obj.message = message
        obj.save()
        return obj

    class Meta:
        fields = [
            "created_by",
            "name",
            "url",
            "force",
            "creator_url",
            "permissions_url",
            "id"
        ]
