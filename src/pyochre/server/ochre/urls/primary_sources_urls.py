import logging
from django.urls import path
from django.views.generic import TemplateView
from pyochre.server.ochre.models import PrimarySource, Query, Annotation


logger = logging.getLogger(__name__)


app_name = "primary_sources"
urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="ochre/template_pack/ochre.html",
            extra_context={
                "items" : [
                    {
                        "title" : "Primary Sources",
                        "model" : PrimarySource,
                        "view_name" : "api:primarysource-list",
                        "creation_methods" : [
                            {
                                "title" : "Create from XSL transformation",
                                "url" : "api:primarysource-create_from_xsl_transformation"
                            },
                            {
                                "title" : "Create from HathiTrust Collection",
                                "url" : "api:primarysource-create_from_hathitrust_collection"
                            }
                        ]
                    },
                    {
                        "title" : "Queries",
                        "model" : Query,
                        "view_name" : "api:query-list",
                        "creation_methods" : [
                            {
                                "title" : "Write in-browser",
                                "url" : "api:query-create_from_text"
                            },
                            {
                                "title" : "Upload",
                                "url" : "api:query-create_from_file"
                            }
                        ]
                    }
                ],
                "uid" : "primary_sources"
            }
        ),
        name="primary_sources"
    )
]
