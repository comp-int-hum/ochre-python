
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetView
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.urls import path
from django.conf import settings
from django.urls import include
from django.views.generic import TemplateView
from django_registration.backends.activation.views import RegistrationView
from django.conf.urls.static import static
from rest_framework.schemas import get_schema_view
from pyochre.server.ochre.forms import UserCreateForm
from pyochre.server.ochre.views import PermissionsView, MarkdownView, SparqlView
from pyochre.server.ochre.routers import OchreRouter
from pyochre.server.ochre.viewsets import OchreViewSet, PrimarySourceViewSet, MaterialViewSet, DocumentationViewSet, UserViewSet, MachineLearningModelViewSet, QueryViewSet, SlideViewSet, ResearchArtifactViewSet, AnnotationViewSet, PermissionsViewSet
from pyochre.server.ochre.models import ResearchArtifact
from pyochre.server.ochre.serializers import ResearchArtifactSerializer


logger = logging.getLogger(__name__)


User = get_user_model()


class CustomPasswordResetView(PasswordResetView):
    @method_decorator(csrf_protect)
    def dispatch(self, *argv, **argd):
        if self.extra_email_context == None:
            self.extra_email_context = {"request" : argv[0]}
        else:
            self.extra_email_context["request"] = argv[0]
        return super(
            CustomPasswordResetView,
            self
        ).dispatch(*argv, **argd)


router = OchreRouter()
for vs in [
        SlideViewSet,
        ResearchArtifactViewSet,
        AnnotationViewSet,
        QueryViewSet,
        PrimarySourceViewSet,
        MachineLearningModelViewSet,
        MaterialViewSet,
        UserViewSet,
        DocumentationViewSet,
        ]:    
    name = vs.schema.component_name
    router.register(name, vs, name)


app_name = "ochre"
urlpatterns = [

    path(
        '',
        TemplateView.as_view(
            template_name="ochre/index.html",
            extra_context={
                "include" : "api:slide-list",
                "style" : "slideshow",
                "image_field" : "image",
                "content_field" : "article"
            }
        ),
        name="index"
    ),
    path(
        'about/',
        TemplateView.as_view(
            template_name="ochre/about.html"
        ),
        name="about"
    ),
    path(
        "wiki/",
        include("wiki.urls"),
        name="wiki"
    ),
    path(
        'people/',
        TemplateView.as_view(
            template_name="ochre/index.html",
            extra_context={"include" : "api:user-list"}
        ),
        name="people"
    ),
    path(
        'research/',
        TemplateView.as_view(
            template_name="ochre/index.html",
            extra_context={
                "include" : "api:researchartifact-list",
                "create" : {
                    "model" : ResearchArtifact,
                    "serializer" : ResearchArtifactSerializer
                }
            }
        ),
        name="researchartifact_list"
    ),
    path(
        "primary_sources/",
        include("pyochre.server.ochre.urls.primary_sources_urls")
    ),
    path(
        "machine_learning/",
        include("pyochre.server.ochre.urls.machine_learning_urls")
    ),
    path(
        "scholarly_knowledge/",
        include("pyochre.server.ochre.urls.scholarly_knowledge_urls")
    ),
    
    # account-related end-points
    path(
        'accounts/register/',
        RegistrationView.as_view(
            form_class=UserCreateForm,
        ),
        name='django_registration_register',
    ),
    path(
        'accounts/password_reset/',
        CustomPasswordResetView.as_view()
    ),
    path(
        'accounts/',
        include('django_registration.backends.activation.urls')
    ),
    path(
        'accounts/',
        include('django.contrib.auth.urls')
    ),

    # legacy special purpose end-points
    path(
       "markdown/",
       MarkdownView.as_view(),
       name="markdown"
    ),
    path(
       "sparql/",
       SparqlView.as_view(),
       name="sparql"
    ),
    path(
       'permissions/<str:app_label>/<str:model>/<int:pk>/',
       PermissionsView.as_view(),        
       name="permissions"
    ),    
    
    # api-related
    path(
        "api/",
        include(
            (router.urls, "api")
        )
    ),
    path(
        'openapi/',
        get_schema_view(
            title="Programmatic Interface",
            description="API for OCHRE server",
            version="1.0.0",
        ),
        name='openapi-schema'
    )
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns.append(
        path(
            '__debug__/',
            include('debug_toolbar.urls')
        )
    )
