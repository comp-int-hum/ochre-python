import logging
from django.db.models.fields.related import ForeignKey
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField, IntegerField, BooleanField, HyperlinkedRelatedField
from pyochre.server.ochre.models import ResearchProject, User
from pyochre.server.ochre.serializers import OchreSerializer
#, UserSerializer


logger = logging.getLogger(__name__)


class ResearchProjectSerializer(OchreSerializer):
    #description = MarkdownEditorField(
    #    language="markdown",
    #    property_field="description",
    #    allow_blank=True,
    #    required=False,
    #    endpoint="markdown"
    #)
    #researchers = UserSerializer(many=True, required=False)
    researchers = HyperlinkedRelatedField(
        many=True,
        view_name="api:user-detail",
        queryset=User.objects.all()
    )
 
    url = HyperlinkedIdentityField(
        view_name="api:researchproject-detail",
        lookup_field="id",
        lookup_url_kwarg="pk"
    )
    #force = BooleanField(
    #    required=False,
    #    write_only=True,
    #    allow_null=True,
    #    default=False,
    #    help_text="Overwrite any existing research project of the same name and creator"
    #    )
    #name = CharField()
    class Meta(OchreSerializer.Meta):
        model = ResearchProject
        fields = [
            "title",
            "abstract",            
            "content",
            "thumbnail",
            "researchers",
            #"artifacts"
        ] + OchreSerializer.Meta.fields
        # fields = [
        #     f.name for f in ResearchProject._meta.fields if not isinstance(f, ForeignKey)
        # ] + [
        #     "name",
        #     "url",
        #     "created_by",
        #     "creator_url",
        #     "force",
        #     "is_active"
        # ]

    # def create(self, validated_data):
    #     if validated_data.get("force", False):
    #         for existing in ResearchProject.objects.filter(
    #                 name=validated_data["name"],
    #                 created_by=validated_data["created_by"]
    #         ):
    #             existing.delete()
    #     validated_data.pop("force")
    #     return super(ResearchProjectSerializer, self).create(validated_data)

        
    def creation_methods(self):
        return [
            {
                "title" : "Add a research project",
                "url" : "api:researchproject-list"
            }
        ]
        # #view_fields = ["description"]
        # edit_fields = [
        #     f.name for f in ResearchProject._meta.fields if not isinstance(f, ForeignKey)
        # ] + [
        #     "url",
        #     "created_by"
        # ]
        # create_fields = [
        #     f.name for f in ResearchProject._meta.fields if not isinstance(f, ForeignKey)
        # ] + [
        #     "url",
        #     "created_by"
        # ]
        #extra_kwargs = dict([(f, {"required" : False}) for f in fields])
