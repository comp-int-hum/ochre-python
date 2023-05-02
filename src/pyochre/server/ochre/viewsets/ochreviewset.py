import logging
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from guardian.shortcuts import get_perms, get_objects_for_user, get_anonymous_user, get_groups_with_perms, get_users_with_perms
from pyochre.server.ochre.renderers import OchreTemplateHTMLRenderer
from pyochre.server.ochre.content_negotiation import OchreContentNegotiation
from pyochre.server.ochre.models import Slide, User
from pyochre.server.ochre.autoschemas import OchreAutoSchema

logger = logging.getLogger(__name__)


class OchreViewSet(ModelViewSet):


    content_negotiation_class = OchreContentNegotiation
    renderer_classes = [
        BrowsableAPIRenderer,
        JSONRenderer,
        OchreTemplateHTMLRenderer
    ]
    detail_template_name = "ochre/template_pack/ochre.html"
    list_template_name = "ochre/template_pack/accordion.html"
    slideshow_template_name = "ochre/template_pack/slideshow.html"
    model = None
    exclude = {}
    accordion_header_template_name = None

    def __init__(self, *argv, **argd):
        super(ModelViewSet, self).__init__(*argv, **argd)
    
    def get_queryset(self):
        perms = "{}_{}".format(
            "delete" if self.action == "destroy"
            else "add" if self.action == "create"
            else "change" if self.action in ["update", "partial_update"]
            else "view" if self.action in ["retrieve", "list"]
            else "view",
            self.model._meta.model_name
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
        ).exclude(
            **self.exclude
        )

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
        self.template_name = self.list_template_name if self.action == "list" else self.detail_template_name
        self.request = request
        self.uid = self.request.headers.get("uid", "1")
        self.style = self.request.headers.get("style")
        self.mode = self.request.headers.get("mode")
        if self.style == "slideshow":
            self.template_name = self.slideshow_template_name
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
        context["model"] = self.model
        context["model_name"] = self.model._meta.verbose_name.title()
        context["model_name_plural"] = self.model._meta.verbose_name_plural.title()
        context["model_perms"] = self.model_perms
        context["uid"] = self.uid
        context["style"] = self.style
        if self.style == "slideshow":
            context["image_field"] = self.request.headers.get("image_field")
            context["content_field"] = self.request.headers.get("content_field")
            context["slide_model"] = Slide
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

    def list(self, request):
        logger.info("List invoked by %s", request.user)
        if request.accepted_renderer.format == "ochre":
            context = self.get_renderer_context()
            return Response(context)
        else:
            return super(OchreViewSet, self).list(request)
        
    def create(self, request):
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
        ):
            logger.info("Permission verified")
            try:
                retval = super(OchreViewSet, self).create(request)
            except Exception as e:
                logging.warn(
                    "Exception in create method of OchreViewSet: %s",
                    e
                )
                raise e
            pk = retval.data["id"]
            if request.accepted_renderer.format == "ochre":
                retval = HttpResponse()
                retval.headers["HX-Trigger"] = """{{"ochreEvent" : {{"event_type" : "create", "model_class" : "{app_label}-{model_name}", "object_class" : "{app_label}-{model_name}-{pk}", "model_url" : "{model_url}"}}}}""".format(
                    app_label=self.model._meta.app_label,
                    model_name=self.model._meta.model_name,
                    pk=pk,
                    model_url=self.model.get_list_url()
                )                
            return retval
        else:
            raise exceptions.PermissionDenied(
                detail="{} does not have permission to create {}".format(
                    request.user,
                    self.model._meta.model_name
                ),
                code=status.HTTP_403_FORBIDDEN
            )

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        #if obj == None:
        #    logger.info("Retrieve invoked by %s", request.user)
        #    ser = self.get_serializer()
        #else:
        logger.info("Retrieve of %s invoked by %s", obj, request.user)
        ser = self.get_serializer()
        return Response(ser.data)

    def destroy(self, request, pk=None):
        logger.info("Delete invoked by %s for %s", request.user, pk)
        retval = super(OchreViewSet, self).destroy(request, pk)        
        retval = HttpResponse()
        if request.accepted_renderer.format == "ochre":
            retval.headers["HX-Trigger"] = """{{"ochreEvent" : {{"event_type" : "delete", "model_class" : "{app_label}-{model_name}", "object_class" : "{app_label}-{model_name}-{pk}"}}}}""".format(
                app_label=self.model._meta.app_label,
                model_name=self.model._meta.model_name,
                pk=pk
            )
        return retval
        
    def update(self, request, pk=None, partial=False):
        logger.info("Update invoked by %s for %s", request.user, pk)
        if self.model.get_change_perm() in get_perms(
                request.user,
                self.get_object()
        ):
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
        
    # @action(detail=True, methods=["get", "patch"])
    # def permissions(self, request, pk=None):
    #     obj = self.model.objects.get(id=pk)
    #     retval = {}
    #     user_perms = get_users_with_perms(
    #         obj,
    #         with_group_users=False,
    #         attach_perms=True
    #     )
    #     group_perms = get_groups_with_perms(
    #         obj,
    #         attach_perms=True
    #     )
    #     retval["user_permissions_options"] = [
    #         (u.get_absolute_url(), [p.split("_")[0] for p in user_perms.get(u, [])]) for u in User.objects.all()
    #     ]
    #     retval["group_permissions_options"] = [
    #         (g.id, [p.split("_")[0] for p in group_perms.get(g, [])]) for g in Group.objects.all()
    #     ]
    #     retval["perms"] = ["delete", "view", "change"]
    #     return Response(retval)
