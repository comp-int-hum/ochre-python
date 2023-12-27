import logging
from django.db.models.fields.related import ForeignKey
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField, IntegerField, BooleanField, HyperlinkedRelatedField
from pyochre.server.ochre.models import ResearchArtifact, ResearchProject, User
from pyochre.server.ochre.serializers import OchreSerializer
#, UserSerializer, ResearchProjectSerializer


logger = logging.getLogger(__name__)


class ResearchArtifactSerializer(OchreSerializer):
    url = HyperlinkedIdentityField(
        view_name="api:researchartifact-detail",
        lookup_field="id",
        lookup_url_kwarg="pk"
    )
    contributors = HyperlinkedRelatedField(
        many=True,
        view_name="api:user-detail",
        queryset=User.objects.all()
    )

    related_to = HyperlinkedRelatedField(
        many=True,
        view_name="api:researchproject-detail",
        queryset=ResearchProject.objects.all()
    )
    class Meta(OchreSerializer.Meta):
        model = ResearchArtifact
        fields = [            
            f.name for f in ResearchArtifact._meta.fields
        ] + ["contributors", "related_to"] + OchreSerializer.Meta.fields
