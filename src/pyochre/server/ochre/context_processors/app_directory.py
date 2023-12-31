import logging
from django.conf import settings
from pyochre.server.ochre.models import Page
from guardian.shortcuts import get_objects_for_user


logger = logging.getLogger(__name__)


def app_directory(request):
    current_page = request.path.rstrip("/").split("/")[-1]
    current_page = current_page if current_page else "index"
    return {
        "apps" : settings.APPS,
        "messages" : [],
        "current_page" : current_page,
        "interaction_name" : settings.APPS.get(current_page, "Ontology" if current_page == "ontology" else "API"),
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
