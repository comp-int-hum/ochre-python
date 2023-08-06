import logging
from django.db.models import UniqueConstraint
from django.urls import path, reverse
from django.db.models import Model, CharField, DateTimeField, ForeignKey, SET_NULL
from pyochre.server.ochre.models import MetadataMixin


logger = logging.getLogger(__name__)


class OchreModel(MetadataMixin, Model):
    name = CharField(max_length=2000, null=False)
    created_by = ForeignKey("ochre.User", null=True, on_delete=SET_NULL, editable=False)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    modified_at = DateTimeField(auto_now=True, editable=False)
    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_name_and_user",
                fields=["name", "created_by"]
            )
        ]
        
    def is_object(self):
        return isinstance(self.id, int)

    @classmethod
    def is_model(self):
        return True
    
    def __str__(self):
        return "{} ({})".format(self.name, self.created_by)

    @classmethod
    def model_title_name(cls):
        return cls._meta.verbose_name.title().replace(" ", "")

    def get_absolute_url(self):
        return reverse("api:{}-detail".format(self._meta.model_name), args=(self.id,))

    @classmethod
    def get_create_url(self):
        return reverse("api:{}-list".format(self._meta.model_name))

    def get_permissions_url(self):
        return reverse("api:{}-permissions".format(self._meta.model_name), args=(self.id,))

    @classmethod
    def get_list_url(self):
        return reverse("api:{}-list".format(self._meta.model_name))

    @classmethod
    def get_add_perm(self):
        return "add_{}".format(self._meta.model_name)

    @classmethod
    def get_delete_perm(self):
        return "delete_{}".format(self._meta.model_name)

    @classmethod
    def get_change_perm(self):
        return "change_{}".format(self._meta.model_name)    

    @classmethod
    def get_view_perm(self):
        return "view_{}".format(self._meta.model_name)    

    @classmethod
    def model_title_singular(self):
        return self._meta.verbose_name.title()

    def model_title_plural(self):
        return self._meta.verbose_name_plural.title()

    @classmethod
    def model_class(self):
        return "{}-{}".format(self._meta.app_label, self._meta.model_name)

    @property
    def object_class(self):
        return "{}-{}-{}".format(self._meta.app_label, self._meta.model_name, self.id)

    @property
    def creator_url(self):
        return self.created_by.get_absolute_url()
