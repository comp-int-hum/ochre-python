import logging
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from pyochre.server.ochre.models import User, Documentation


logger = logging.getLogger(__name__)


def app_directory(request):
    top_level = request.path.lstrip("/").split("/")[0]
    return {
        "flat_pages" : [p for p in FlatPage.objects.all() if re.match(r"^\/[^\/]+\/$", p.url)],
        "is_admin" : request.user.is_staff or request.user.groups.filter(name="web").exists(),
        "apps" : settings.APPS,
        "builtin_pages" : settings.BUILTIN_PAGES,
        "messages" : [],
        "top_level" : top_level,
        "interaction_name" : settings.APPS.get(top_level, "Ontology" if top_level == "ontology" else "API"),
        "documentation_model" : Documentation,
    }
