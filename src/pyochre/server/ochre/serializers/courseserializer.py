import logging
from collections import OrderedDict
from django.db.models.fields.related import ForeignKey
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField, IntegerField, BooleanField, HyperlinkedRelatedField
from pyochre.server.ochre.models import Course, User
from pyochre.server.ochre.serializers import OchreSerializer, UserSerializer
from pyochre.server.ochre.fields import MonacoEditorField


logger = logging.getLogger(__name__)


class InstructorField(HyperlinkedRelatedField):
    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            # Ensure that field.choices returns something sensible
            # even when accessed with a read-only field.
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict([
            (
                self.to_representation(item),
                item
                #[self.display_value(item), item.id]
                #OrderedDict([("name", self.display_value(item)), ("id", item.id)])
            )
            for item in queryset
        ])


class CourseSerializer(OchreSerializer):
    url = HyperlinkedIdentityField(
        view_name="api:course-detail",
        lookup_field="id",
        lookup_url_kwarg="pk"
    )
    instructors = InstructorField(
        many=True,
        view_name="api:user-detail",
        queryset=User.objects.all()
    )
    description = MonacoEditorField(
        label="Description",
        language="markdown",
        property_field="description",
        allow_blank=True,
        required=False,
    )

    class Meta(OchreSerializer.Meta):
        model = Course
        fields = [
            "title",
            "identifier",
            "description",
            "instructors",
            "ordering"
        ] + OchreSerializer.Meta.fields
