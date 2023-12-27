import logging
from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.viewsets import ViewSet
from guardian.shortcuts import get_objects_for_user, get_users_with_perms, get_groups_with_perms
from pyochre.server.ochre.autoschemas import OchreAutoSchema
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.serializers import PermissionsSerializer


logger = logging.getLogger(__name__)


class PermissionsViewSet(OchreViewSet):

    schema = OchreAutoSchema(
        tags=["permissions"],
        component_name="permissions",
        operation_id_base="permissions"
    )

    serializer_class = PermissionsSerializer

    def retrieve(self, request, pk=None):
        return Response(200)

    def update(self, request, pk=None):
        ctx = self.get_context_data()
        for ptype in ["user", "group"]:
            for option, _ in ctx.get(
                    "{}_permissions_options".format(
                        ptype
                    ),
                    []
            ):
                for perm in ctx.get("perms", []):
                    if str(option.id) in request.POST.getlist(
                            "{}_{}".format(ptype, perm),
                            []
                    ):
                        to_add = "{}_{}".format(
                            perm,
                            option._meta.model_name
                        )
                        assign_perm(
                            "{}_{}".format(
                                perm,
                                self.model._meta.model_name
                            ),
                            option,
                            self.object
                        )
                    else:
                        to_remove = "{}_{}".format(
                            perm,
                            option._meta.model_name
                        )
                        remove_perm(
                            "{}_{}".format(
                                perm,
                                self.model._meta.model_name
                            ),
                            option,
                            self.object
                        )
        return Response(200)
                        
    def perms(self, user, model, obj):
        retval = {}
        user_perms = get_users_with_perms(
            obj,
            with_group_users=False,
            attach_perms=True
        )
        group_perms = get_groups_with_perms(
            obj,
            attach_perms=True
        )
        retval["user_permissions_options"] = [
            (
                u,
                [p.split("_")[0] for p in user_perms.get(u, [])]
             ) for u in User.objects.all()
        ]
        retval["group_permissions_options"] = [
            (
                g,
                [p.split("_")[0] for p in group_perms.get(g, [])]
            ) for g in Group.objects.all()
        ]
        retval["perms"] = ["delete", "view", "change"]
        return retval
        
    
