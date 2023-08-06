import logging
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from guardian.shortcuts import get_perms, get_objects_for_user, get_anonymous_user, get_groups_with_perms, get_users_with_perms, remove_perm, assign_perm
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
from pyochre.server.ochre.content_negotiation import OchreContentNegotiation
from pyochre.server.ochre.models import User
from pyochre.server.ochre.autoschemas import OchreAutoSchema
from pyochre.server.ochre.serializers import PermissionsSerializer
from pyochre.server.ochre.permissions import OchrePermissions
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework_guardian.filters import ObjectPermissionsFilter


logger = logging.getLogger(__name__)


class OchreViewSet(GenericViewSet):
    content_negotiation_class = OchreContentNegotiation
    renderer_classes = [
        BrowsableAPIRenderer,
        JSONRenderer,
        OchreTemplateHTMLRenderer
    ]
    detail_template_name = "ochre/template_pack/generic_detail.html"
    edit_template_name = "ochre/template_pack/generic_edit.html"
    create_template_name = "ochre/template_pack/generic_create.html"    
    #permission_classes = [OchrePermissions]
    #filter_backends = [ObjectPermissionsFilter]
    #list_template_name = "ochre/template_pack/ochre.html"
    list_template_name = "ochre/template_pack/accordion.html"
    accordion_header_template_name = "ochre/template_pack/accordion_header.html"
    accordion_content_template_name = "ochre/template_pack/accordion_content.html"

    def __init__(self, *argv, **argd):
        super(OchreViewSet, self).__init__(*argv, **argd)    

    def get_template_names(self):
        if self.template_override:
            return [self.template_override]
        if self.mode == "edit":
            retval = [self.edit_template_name]
        elif self.request.headers.get("mode") == "create":
            retval = [self.create_template_name]            
        elif self.action == "list":
            retval = [self.list_template_name]
        elif self.action == "retrieve":
            retval = [self.detail_template_name]
        else:
            retval = [self.detail_template_name]
        logger.info("Using template '%s' for %s on %s", retval[0], self.action, self.model)
        return retval
    
    def get_queryset(self):
        perms = "{}_{}".format(
            "delete" if self.action == "destroy"
            else "add" if self.action == "create"
            else "change" if self.action in ["update", "partial_update"]
            else "view" if self.action in ["retrieve", "list"]
            else "view",
            self.model._meta.model_name if self.model else ""
        )
        return (
            get_objects_for_user(
                get_anonymous_user(),
                perms=perms,
                klass=self.model
            ) | get_objects_for_user(
                self.request.user,
                perms=perms,
                klass=self.model
            )
        ) if self.model else []

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        if self.kwargs[lookup_url_kwarg] == "None":
            return None
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)        
        return obj

    def initialize_request(self, request, *argv, **argd):
        retval = super(
            OchreViewSet,
            self
        ).initialize_request(
            request,
            *argv,
            **argd
        )

        self.request = request
        self.uid = self.request.headers.get("uid", "1")
        self.template_override = self.request.headers.get("template")
        #self.scope = "list" if self.action == "list" else "detail"
        self.mode = self.request.headers.get("mode", "view")
        #self.location = self.request.headers.get("location", "standalone")
        self.method = self.request.method
        self.from_htmx = self.request.headers.get("Hx-Request", False) and True
        if self.model:
            self.app_label = self.model._meta.app_label
            self.model_name = self.model._meta.model_name
            self.model_perms = ["add"] if self.request.user.has_perm(
                "{}.add_{}".format(self.app_label, self.model_name)
            ) else []
        return retval

    def get_renderer_context(self, *argv, **argd):
        context = super(OchreViewSet, self).get_renderer_context(*argv, **argd)
        context["mode"] = self.mode
        if self.model:
            context["model"] = self.model
            context["model_name"] = self.model._meta.verbose_name.title()
            context["model_name_plural"] = self.model._meta.verbose_name_plural.title()
            context["model_perms"] = self.model_perms
        context["uid"] = self.uid
        if self.detail:
            obj = self.get_object()
            if obj != None:
                context["serializer"] = self.get_serializer(obj)
                context["object"] = obj
            else:
                context["serializer"] = self.get_serializer()
        elif self.action == "create":
            context["serializer"] = self.get_serializer()
        elif not self.detail:
            context["serializer"] = self.get_serializer()
            context["items"] = self.get_queryset()
            context["accordion_header_template_name"] = self.accordion_header_template_name
        else:
            raise Exception("Incoherent combination of detail/action on OchreViewSet")
        logger.info("Accepted renderer: %s", self.request.accepted_renderer)
        context["viewset"] = self
        context["request"] = self.request
        return context

    def _list(self, request):
        logger.info("List invoked by %s", request.user)
        ser = self.get_serializer_class()(
            #ser = scl(
            self.get_queryset(),
            many=True,
            context={"request" : request}
        )
        #if request.accepted_renderer.format == "ochre":
        #    context = self.get_renderer_context()
        #    return Response(context)
        #print(ser.data)
        return Response(ser.data)
        
    def _create(self, request):
        logger.info(
            "Create %s invoked by %s",
            self.model._meta.model_name,
            request.user
        )
        if request.user.has_perm(
                "{}.add_{}".format(
                    self.model._meta.app_label,
                    self.model._meta.model_name
                )
        ) or request.user.is_staff:
            logger.info("Permission verified")
            try:
                ser = self.get_serializer_class()(
                    data=request.data,
                    context={"request" : request}
                )
                if ser.is_valid():
                    obj = ser.create(ser.validated_data)
                    resp_ser = self.get_serializer_class()(
                        obj,
                        context={"request" : request}
                    )
                    return Response(resp_ser.data)
                else:
                    return Response(
                        ser.errors,
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                logging.warn(
                    "Exception in create method of OchreViewSet: %s",
                    e
                )
                raise e
            pk = retval.data["id"]
            # if request.accepted_renderer.format == "ochre":
            #     retval = HttpResponse()
            #     retval.headers["HX-Trigger"] = """{{"ochreEvent" : {{"event_type" : "create", "model_class" : "{app_label}-{model_name}", "object_class" : "{app_label}-{model_name}-{pk}", "model_url" : "{model_url}"}}}}""".format(
            #         app_label=self.model._meta.app_label,
            #         model_name=self.model._meta.model_name,
            #         pk=pk,
            #         model_url=self.model.get_list_url()
            #     )                
            # return retval
        else:
            raise exceptions.PermissionDenied(
                detail="{} does not have permission to create {}".format(
                    request.user,
                    self.model._meta.model_name
                ),
                code=status.HTTP_403_FORBIDDEN
            )

    def _retrieve(self, request, pk=None):
        obj = self.get_object()
        logger.info("Retrieve of %s invoked by %s", obj, request.user)
        ser = self.get_serializer_class()(obj, context={"request" : request})
        logger.info("Using serializer class:  %s", type(ser).__name__)
        return Response(ser.data)
    
    def _destroy(self, request, pk=None):
        logger.info("Delete invoked by %s for %s", request.user, pk)
        obj = self.get_queryset().get(id=pk)
        string_rep = str(obj)
        obj.delete()
        retval = JsonResponse(
            {
                "description" : "Deleted object '{}'".format(string_rep),
            }
        )
        if request.accepted_renderer.format == "ochre":
            retval.headers["HX-Trigger"] = """{{"ochreEvent" : {{"event_type" : "delete", "model_class" : "{app_label}-{model_name}", "object_class" : "{app_label}-{model_name}-{pk}"}}}}""".format(
                app_label=self.model._meta.app_label,
                model_name=self.model._meta.model_name,
                pk=pk
            )
        return retval

    def _update(self, request, pk=None, partial=False):
        logger.info("Update invoked by %s for %s", request.user, pk)
        if self.model.get_change_perm() in get_perms(
                request.user,
                self.get_object()
        ) or request.user.is_staff:
            logger.info("Permission verified")
            retval = super(OchreViewSet, self).update(request, pk)
            retval.headers["HX-Trigger"] = """{{"ochreEvent" : {{"event_type" : "update", "model_class" : "{app_label}-{model_name}", "object_class" : "{app_label}-{model_name}-{pk}"}}}}""".format(
                app_label=self.model._meta.app_label,
                model_name=self.model._meta.model_name,
                pk=pk
            )                
            return retval
        else:
            raise exceptions.PermissionDenied(
                detail="{} does not have permission to change {} object {}".format(
                    request.user,
                    self.model._meta.model_name,
                    pk
                ),
                code=status.HTTP_403_FORBIDDEN
            )
    
    def _partial_update(self, request, pk=None, partial=False):
        logger.info("Partial update invoked by %s for %s", request.user, pk)
        if self.model.get_change_perm() in get_perms(
                request.user,
                self.get_object()
        ) or request.user.is_staff:
            logger.info("Permission verified")
            obj = self.get_queryset().get(id=pk)
            ser = self.get_serializer_class()(
                obj,
                data=request.data,
                partial=True,
                context={"request" : request}
            )
            if ser.is_valid():
                #retval = super(OchreViewSet, self).update(request, pk, partial=True)
                #return retval
                #print(ser.validated_data)
                #return Response(ser.save())
                nobj = ser.partial_update(obj, request.data)
                nser = self.get_serializer_class()(obj, context={"request" : request})
                return Response(nser.data)
                #retval.headers["HX-Redirect"] = obj.get_absolute_url()
                #print(retval)
                
                #retval = super(OchreViewSet, self).update(request, pk)
                #retval.headers["HX-Trigger"] = """{{"ochreEvent" : {{"event_type" : "update", "model_class" : "{app_label}-{model_name}", "object_class" : "{app_label}-{model_name}-{pk}"}}}}""".format(
                #    app_label=self.model._meta.app_label,
                #    model_name=self.model._meta.model_name,
                #    pk=pk
                #)                
                return retval
            else:
                logger.error("Errors in partial update: %s", ser.errors)
                return Response(
                    ser.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            raise exceptions.PermissionDenied(
                detail="{} does not have permission to change {} object {}".format(
                    request.user,
                    self.model._meta.model_name,
                    pk
                ),
                code=status.HTTP_403_FORBIDDEN
            )

        
    def _permissions(self, request, pk=None):
        all_permissions = ["delete", "view", "change"]
        ser = PermissionsSerializer(
            data=request.data,
            context={
                "request" : request,
                "pk" : pk,
                "model" : self.model
            }
        )
        if ser.is_valid():
            data = {k : v for k, v in ser.data.items()}
            if request.method == "PATCH":
                data["user_permissions"] = {}
                data["group_permissions"] = {}
                for k in request.data.keys():
                    etype, ptype = k.split("_")
                    data["{}_permissions".format(etype)][ptype] = [int(x) for x in request.data.getlist(k)]
                obj = self.model.objects.get(id=pk)
                for ptype in all_permissions:
                    entries = data.get("user_permissions", {}).get(ptype, [])                    
                    perm = "{}_{}".format(ptype, self.model._meta.model_name)
                    for u in User.objects.all():
                        if u.id in entries:
                            assign_perm(perm, u, obj)
                        else:
                            remove_perm(perm, u, obj)
                for ptype in all_permissions:
                    entries = data.get("group_permissions", {}).get(ptype, [])
                    perm = "{}_{}".format(ptype, self.model._meta.model_name)                    
                    for g in Group.objects.all():
                        if g.id in entries:
                            assign_perm(perm, g, obj)
                        else:
                            remove_perm(perm, g, obj)
                return Response(ser.data, status=status.HTTP_200_OK)
            elif request.method == "GET":
                data["all_users"] = [[u.id, u.username] for u in User.objects.all()]
                data["all_groups"] = [[g.id, g.name] for g in Group.objects.all()]
                data["all_permissions"] = ["delete", "view", "change"]
                return Response(data, template_name="ochre/template_pack/permissions.html")
        else:
            return Response(
                ser.errors,
                status=status.HTTP_400_BAD_REQUEST
            )        
