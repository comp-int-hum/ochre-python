import logging
from django.db.models.fields.related import ForeignKey
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField, IntegerField, BooleanField, HyperlinkedRelatedField
from pyochre.server.ochre.models import ResearchProject, User
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import MonacoEditorField


logger = logging.getLogger(__name__)


class ResearchProjectSerializer(OchreSerializer):

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
    content = MonacoEditorField(
        label="Full description",
        language="markdown",
        property_field="content",
        allow_blank=True,
        required=False,
    )

    class Meta(OchreSerializer.Meta):
        model = ResearchProject
        fields = [
            "title",
            "abstract",            
            "content",
            "thumbnail",
            "researchers",
        ] + OchreSerializer.Meta.fields
        
    def creation_methods(self):
        return [
            {
                "title" : "Add a research project",
                "url" : "api:researchproject-list"
            }
        ]
