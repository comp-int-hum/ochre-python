import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetView
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.urls import path, re_path
from django.conf import settings
from django.urls import include
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.views.generic import TemplateView, DetailView
from django_registration.backends.activation.views import RegistrationView
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from rest_framework.schemas import get_schema_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from pyochre.server.ochre.forms import UserCreateForm
from pyochre.server.ochre.routers import OchreRouter
from pyochre.server.ochre.viewsets import OchreViewSet, PrimarySourceViewSet, MaterialViewSet, UserViewSet, MachineLearningModelViewSet, QueryViewSet, ArticleViewSet, ResearchArtifactViewSet, AnnotationViewSet, PermissionsViewSet, OntologyViewSet, CourseViewSet, ResearchProjectViewSet, PageViewSet, FileViewSet
from pyochre.server.ochre.models import ResearchArtifact, Article, Course, ResearchProject, Page
from pyochre.server.ochre.serializers import ResearchArtifactSerializer
from pyochre.server.ochre.schemagenerators import OchreSchemaGenerator


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

# TODO: actions for cleaning, backup, getting namespace
router = OchreRouter()
for vs in [
        ArticleViewSet,
        ResearchArtifactViewSet,
        AnnotationViewSet,
        QueryViewSet,
        PrimarySourceViewSet,
        MachineLearningModelViewSet,
        MaterialViewSet,
        UserViewSet,
        PageViewSet,
        PermissionsViewSet,
        OntologyViewSet,
        ResearchProjectViewSet,
        CourseViewSet,
        FileViewSet
        ]:    
    name = vs.schema.component_name
    router.register(name, vs, name)


app_name = "ochre"
urlpatterns = [
    path(
        'articles/<int:pk>/',
        DetailView.as_view(
            template_name="ochre/template_pack/article_detail_view.html",
            model=Article
        ),
        name="article_detail"
    ),
    path(
        'people/<int:pk>/',
        DetailView.as_view(
            template_name="ochre/template_pack/user_detail_view.html",
            model=User
        ),
        name="user_detail"
    ),
    path(
        'research/<int:pk>/',
        DetailView.as_view(
            template_name="ochre/template_pack/researchproject_detail_view.html",
            model=ResearchProject
        ),
        name="researchproject_detail"
    ),
    path(
        'research_artifacts/<int:pk>/',
        DetailView.as_view(
            template_name="ochre/template_pack/researchartifact_detail.html",
            model=ResearchArtifact
        ),
        name="researchartifact_detail"
    ),
    path(
        'teaching/<int:pk>/',
        DetailView.as_view(
            template_name="ochre/template_pack/course_detail_view.html",
            model=Course
        ),
        name="course_detail"
    ),

    # OCHRE
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
    
    # account-related
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
            generator_class=OchreSchemaGenerator
        ),
        name='openapi-schema'
    ),
    path(
        'ontology/',
        TemplateView.as_view(
            template_name="ochre/template_pack/ochre.html",
            extra_context={"view_name" : "api:ontology-list", "uid" : "ontology"}
        ),
        name='ontology'
    ),
    # path(
    #     'sitemap.xml',
    #     sitemap,
    #     {"sitemaps": {}},
    #     name="django.contrib.sitemaps.views.sitemap",
    # ),    
    re_path(
        '^(\w+/)?$',
        TemplateView.as_view(
            template_name="ochre/template_pack/index.html",
        ),
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
