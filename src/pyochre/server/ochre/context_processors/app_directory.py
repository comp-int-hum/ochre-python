import logging
from django.conf import settings
#from django.contrib.flatpages.models import FlatPage
from pyochre.server.ochre.models import Page #Banner #User, Documentation
from guardian.shortcuts import get_perms, get_objects_for_user, get_anonymous_user, get_groups_with_perms, get_users_with_perms, remove_perm, assign_perm


logger = logging.getLogger(__name__)


def app_directory(request):
    top_level = request.path.lstrip("/").split("/")[0]
    top_level = top_level if top_level else "index"

    return {
        "apps" : settings.APPS,
        "builtin_pages" : settings.BUILTIN_PAGES,
        "messages" : [],
        "top_level" : top_level,
        "page_name" : top_level,
        "interaction_name" : settings.APPS.get(top_level, "Ontology" if top_level == "ontology" else "API"),
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
        "headshot_icon" : settings.HEADSHOT_ICON,
        "permissions_icon" : settings.PERMISSIONS_ICON,
        "pages" : get_objects_for_user(request.user, "view_page", klass=Page)
    }
