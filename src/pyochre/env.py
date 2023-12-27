import environ
import os.path
import logging


env = environ.Env(

    ENVIRONMENT = (str, "env"),

    USER = (str, ""),
    PASSWORD = (str, ""),
    LOG_LEVEL = (str, "INFO"),

    DEBUG = (bool, False),
    
    PROTOCOL = (str, "http"),
    HOSTNAME = (str, "localhost"),
    IP = (str, "127.0.0.1"),
    PORT = (int, 8000),
    API_PATH = (str, "/api"),
    
    DATA_DIR = (str, os.path.expanduser("~/ochre")),
    
    INDEX_TEMPLATE = (str, ""),
    ABOUT_TEMPLATE = (str, ""),
    RESEARCH_TEMPLATE = (str, ""),
    TEACHING_TEMPLATE = (str, ""),
    EVENTS_TEMPLATE = (str, ""),
    PEOPLE_TEMPLATE = (str, ""),

    USE_POSTGRES = (bool, False),
    POSTGRES_HOST = (str, "localhost"),
    POSTGRES_DB_NAME = (str, "ochre"),
    POSTGRES_USER = (str, "ochre"),
    POSTGRES_PASSWORD = (str, "CHANGE_ME"),
    
    USE_CELERY = (bool, False),
    CELERY_BROKER_URL = (str, "redis://localhost:6379"),
    CELERY_RESULT_BACKEND  = (str, "redis://localhost:6379"),

    USE_TORCHSERVE = (bool, False),
    TORCHSERVE_INFERENCE_ADDRESS = (str, "http://127.0.0.1:8080"),
    TORCHSERVE_MANAGEMENT_ADDRESS = (str, "http://127.0.0.1:8081"),
    TORCHSERVE_METRICS_ADDRESS = (str, "http://127.0.0.1:8082"),
    TORCHSERVE_TIMEOUT = (float, 30.0),

    USE_JENA = (bool, False),
    JENA_PROTOCOL = (str, "http"), 
    JENA_HOST = (str, "localhost"),
    JENA_PORT = (int, 3030),
    JENA_USER = (str, "admin"),
    JENA_PASSWORD = (str, "CHANGE_ME"),
    JENA_TIMEOUT = (float, 300.0),

    USE_EMAIL = (bool, False),
    EMAIL_HOST = (str, "smtp.gmail.com"),
    EMAIL_PORT = (int, 587),
    EMAIL_HOST_USER = (str, "jhu.digital.humanities"),
    EMAIL_HOST_PASSWORD = (str, ""),
    EMAIL_USE_TLS = (bool, True),
    EMAIL_WHITELIST = (list, ["tom.lippincott@gmail.com"]),
    
    USE_LDAP = (bool, False),
    LDAP_WEB_GROUP = (str, "web"),
    LDAP_WEB_ADMIN_GROUP = (str, "webadmin"),
    LDAP_WORKSTATION_GROUP = (str, "workstation"),
    LDAP_WORKSTATION_ADMIN_GROUP = (str, "workstationadmin"),
    LDAP_ROOT_BASE_COMPONENTS = (list, ["dc=ochre", "dc=org"]),
    LDAP_USER_BASE_COMPONENTS = (list, ["ou=users"]),
    LDAP_GROUP_BASE_COMPONENTS = (list, ["ou=groups"]),
    LDAP_BIND_PASSWORD = (str, "CHANGE_ME"),
    LDAP_CERT_FILE = (str, ""),
    LDAP_SERVER_URI = (str, "ldap://localhost:389/"),
    
    OCHRE_NAMESPACE = (str, "https://cdh.jhu.edu/"),
    HATHITRUST_ROOT = (str, None),
    STATICFILES_DIRS = (list, []),

    CREATE_ICON = (str, "bi-plus-lg"),
    DELETE_ICON = (str, "bi-trash3"),
    COMMIT_ICON = (str, "bi-check2"),
    CANCEL_ICON = (str, "bi-x"),
    EDIT_ICON = (str, "bi-pencil"),
    LOGIN_ICON = (str, "bi-door-closed"),
    LOGOUT_ICON = (str, "bi-door-open"),
    PHONE_ICON = (str, "bi-telephone-fill"),
    EMAIL_ICON = (str, "bi-envelope-fill"),
    LOCATION_ICON = (str, "bi-geo-alt-fill"),
    HOMEPAGE_ICON = (str, "bi-house-fill"),
    HEADSHOT_ICON = (str, "bi-person-fill"),
    PERMISSIONS_ICON = (str, "bi-lock")
)

env.read_env(env("ENVIRONMENT"), overwrite=True)
logging.basicConfig(level=getattr(logging, env("LOG_LEVEL")))


