import json
import logging
from hashlib import md5
from django.contrib.auth.models import Group
from django.conf import settings
from pairtree import PairtreeStorageFactory
import magic
from rest_framework.serializers import CharField, IntegerField, SerializerMethodField, Serializer, SerializerMethodField, SlugRelatedField
from guardian.shortcuts import get_perms, get_objects_for_user, get_anonymous_user, get_groups_with_perms, get_users_with_perms
from pyochre.server.ochre.models import User


logger = logging.getLogger(__name__)


class PermissionsSerializer(Serializer):
    user_permissions = SerializerMethodField()
    group_permissions = SerializerMethodField()
    
    def get_user_permissions(self, obj):
        self.model = self.context["model"]
        obj = self.model.objects.get(id=self.context["pk"])
        request = self.context["request"]
        user_perms = get_users_with_perms(
            obj,
            with_group_users=False,
            attach_perms=True
        ) if obj else {}
        retval = {"delete" : [], "view" : [], "change" : []}        
        for uid, perms in {
            u.id : [p.split("_")[0] for p in user_perms.get(u, [])] for u in User.objects.all()
        }.items():
            for perm in perms:
                retval[perm] = retval.get(perm, [])
                retval[perm].append(uid)
        return retval
    
    def get_group_permissions(self, obj):
        self.model = self.context["model"]
        obj = self.model.objects.get(id=self.context["pk"])
        request = self.context["request"]
        group_perms = get_groups_with_perms(
            obj,
            attach_perms=True
        ) if obj else {}
        retval = {"delete" : [], "view" : [], "change" : []}
        for gid, perms in {
                g.id : [p.split("_")[0] for p in group_perms.get(g, [])] for g in Group.objects.all()
        }.items():
            for perm in perms:
                retval[perm] = retval.get(perm, [])
                retval[perm].append(gid)
        return retval
