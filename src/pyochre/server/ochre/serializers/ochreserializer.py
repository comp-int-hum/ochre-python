import logging
from django.db.models.fields.related import ForeignKey
from rest_framework.serializers import ModelSerializer, HiddenField, HyperlinkedIdentityField, CurrentUserDefault, CharField, HyperlinkedRelatedField


logger = logging.getLogger(__name__)


class OchreSerializer(ModelSerializer):

    def __init__(self, *argv, **argd):
        for field in self.Meta.model._meta.fields:
            if isinstance(field, ForeignKey) and field.name not in getattr(self.Meta, "exclude", []):
                self.fields[field.name] = HyperlinkedRelatedField(
                    view_name="api:{}-detail".format(
                        field.related_model._meta.model_name
                    ),
                    queryset=field.related_model.objects.all()
                )
        retval = super(OchreSerializer, self).__init__(*argv, **argd)
        self.fields["url"] = HyperlinkedIdentityField(
            view_name="api:{}-detail".format(
                self.Meta.model._meta.model_name
            ),
            lookup_field="id",
            lookup_url_kwarg="pk"
        )
        self.fields["created_by"] = HiddenField(            
            default=CurrentUserDefault()
        )
        self.fields["name"] = CharField(
            max_length=2000,
            required=False
        )
        #self.fields["permissions_url"] = HyperlinkedIdentityField(
        #    view_name="api:{}-permissions".format(
        #        self.Meta.model._meta.model_name
        #    )
        #)
        return retval
