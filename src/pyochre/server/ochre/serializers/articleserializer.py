import logging
from rest_framework.serializers import HyperlinkedIdentityField, DateField, HyperlinkedRelatedField
from pyochre.server.ochre.models import Article, ResearchArtifact, User, ResearchProject, Course
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import MonacoEditorField


logger = logging.getLogger(__name__)

    
class ArticleSerializer(OchreSerializer):
    url = HyperlinkedIdentityField(
        view_name="api:article-detail",
        lookup_field="id",
        lookup_url_kwarg="pk",
        read_only=True,
        help_text="URL of this article."
    )
    date = DateField(
    )
    people = HyperlinkedRelatedField(
        many=True,
        view_name="api:user-detail",
        queryset=User.objects.all()
    )
    researchprojects = HyperlinkedRelatedField(
        many=True,
        view_name="api:researchproject-detail",
        queryset=ResearchProject.objects.all()
    )
    courses = HyperlinkedRelatedField(
        many=True,
        view_name="api:course-detail",
        queryset=Course.objects.all()
    )
    researchartifacts = HyperlinkedRelatedField(
        many=True,
        view_name="api:researchartifact-detail",
        queryset=ResearchArtifact.objects.all()
    )
    content = MonacoEditorField(
        label="Full description (may use Markdown)",
        language="markdown",
        property_field="content",
        allow_blank=True,
        required=False,
    )
    class Meta(OchreSerializer.Meta):
        model = Article
        fields = [
            "title",
            "abstract",
            "content",
            "ordering",
            "thumbnail",
            "date",
            "people",
            "researchprojects",
            "courses",
            "researchartifacts"
        ] + OchreSerializer.Meta.fields
