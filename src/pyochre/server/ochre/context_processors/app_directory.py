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
        "create_icon" : settings.CREATE_ICON,
        "cancel_icon" : settings.CANCEL_ICON,
        "commit_icon" : settings.COMMIT_ICON,
        "edit_icon" : settings.EDIT_ICON,
        "delete_icon" : settings.DELETE_ICON,
        "login_icon" : settings.LOGIN_ICON,
        "logout_icon" : settings.LOGOUT_ICON,
        "phone_icon" : settings.PHONE_ICON,
        "email_icon" : settings.EMAIL_ICON,
        "location_icon" : settings.LOCATION_ICON,
        "homepage_icon" : settings.HOMEPAGE_ICON,
        "headshot_icon" : settings.HEADSHOT_ICON
    }
