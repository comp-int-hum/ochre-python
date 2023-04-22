"""
Django settings for the OCHRE project.
"""
from pathlib import Path
import os
import os.path
import environ
import requests

env = environ.Env(

    DEBUG = (bool, False),
    ENVIRONMENT = (str, "env"),
    
    PROTO = (str, "http"),
    HOSTNAME = (str, "localhost"),
    IP = (str, "127.0.0.1"),
    PORT = (int, 8000),
    
    DATA_DIR = (str, os.path.expanduser("~/ochre")),
    
    INDEX_TEMPLATE = (str, ""),
    ABOUT_TEMPLATE = (str, ""),

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
    JENA_PROTO = (str, "http"), 
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
    
    OCHRE_NAMESPACE = (str, "https://cdh.jhu.edu/ontology/"),
)

environ.Env.read_env(env("ENVIRONMENT"))

template_dict = {}

if env("INDEX_TEMPLATE"):
    with open(env("INDEX_TEMPLATE"), "rt") as ifd:
        template_dict["ochre/index.html"] = ifd.read()
        
if env("ABOUT_TEMPLATE"):
    with open(env("ABOUT_TEMPLATE"), "rt") as ifd:
        template_dict["ochre/about.html"] = ifd.read()        

OCHRE_NAMESPACE = env("OCHRE_NAMESPACE")

BUILTIN_PAGES = {
    "about" : "About",
    "people" : "People",
    "research" : "Research",
    "wiki" : "Wiki",
}

APPS = {
    "primary_sources" : "Primary sources",
    "machine_learning" : "Machine learning",
    "scholarly_knowledge" : "Scholarly knowledge",
}



# NOTE: For development you can follow the README instructions for running the needed backends locally,
#       and set these to True, otherwise the framework will use hacks to simulate the behavior
#       (but it may not be identical to the production site).  For a full production setup, the
#       connection information (servers, usernames, passwords, etc) will need to be specified in the
#       appropriate sections below.
USE_LDAP = env("USE_LDAP")
USE_CELERY = env("USE_CELERY")
USE_POSTGRES = env("USE_POSTGRES")
#USE_JENA = env("USE_JENA")
#USE_TORCHSERVE = env("USE_TORCHSERVE")

# NOTE: These should be fine for development, but for deployment would need to be changed to match
#       the server the framework runs on.
HOSTNAME = env("HOSTNAME")
IP = env("IP")#
PORT = env("PORT")

# NOTE: To perform two-stage account creation the framework needs the ability to send emails.  The
#       development default is to not send emails, just write them to the console, which allows you
#       to test functionality etc.  To enable actual emails, comment the following line, uncomment
#       the rest starting with "EMAIL", and edit the values as necessary (they are correct for sending
#       emails, except for the password, which should only be filled in on the
#       production server)

USE_EMAIL = env("USE_EMAIL")
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' if USE_EMAIL else 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_WHITELIST = env("EMAIL_WHITELIST")


USE_CELERY = env("USE_CELERY")
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = "UTC"


USE_TORCHSERVE = env("USE_TORCHSERVE")
TORCHSERVE_INFERENCE_ADDRESS = env("TORCHSERVE_INFERENCE_ADDRESS")
TORCHSERVE_MANAGEMENT_ADDRESS = env("TORCHSERVE_MANAGEMENT_ADDRESS")
TORCHSERVE_METRICS_ADDRESS = env("TORCHSERVE_METRICS_ADDRESS")
TORCHSERVE_TIMEOUT = env("TORCHSERVE_TIMEOUT")


USE_JENA = env("USE_JENA")
JENA_PROTO = env("JENA_PROTO")
JENA_HOST = env("JENA_HOST")
JENA_PORT = env("JENA_PORT")
JENA_URL = "{}://{}:{}".format(JENA_PROTO, JENA_HOST, JENA_PORT)
JENA_USER = env("JENA_USER")
JENA_PASSWORD = env("JENA_PASSWORD")
JENA_TIMEOUT = env("JENA_TIMEOUT")
if USE_JENA:
    resp = requests.get(
        "{}/$/stats".format(JENA_URL),
        auth=requests.auth.HTTPBasicAuth(JENA_USER, JENA_PASSWORD),
    ).json()
    if "/ochre" not in resp["datasets"]:
        requests.post(            
            "{}/$/datasets".format(JENA_URL),
            data={
                "dbType" : "tdb",
                "dbName" : "ochre"
            },
            auth=requests.auth.HTTPBasicAuth(JENA_USER, JENA_PASSWORD)
        )


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# NOTE: This directory is where all significant data not managed
# by Postgres or Jena will be stored.  By default, for development,
# it's set to a "ochre" subdirectory of the user's home directory,
# but in production it should be set to something more appropriate,
# with lots of free space.  Note that it will be created if it doesn't
# exist yet.
DATA_DIR = Path(env("DATA_DIR"))
STATIC_ROOT = DATA_DIR / "static"
MEDIA_ROOT = DATA_DIR / "media"
TEMP_ROOT = DATA_DIR / "temp"
MATERIALS_ROOT = DATA_DIR / "materials"
MODELS_ROOT = DATA_DIR / "models"
RDF_ROOT = DATA_DIR / "rdf"
for path in [DATA_DIR, STATIC_ROOT, MEDIA_ROOT, TEMP_ROOT, MATERIALS_ROOT, MODELS_ROOT, RDF_ROOT]:
    if not path.exists():
        path.mkdir()
        
# NOTE: We don't impose upload limits, because it's expected that
# people will upload datasets.
FILE_UPLOAD_MAX_MEMORY_SIZE = 262144000
DATA_UPLOAD_MAX_MEMORY_SIZE = None
TURKLE_TEMPLATE_LIMIT = 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
MATERIALS_TIMEOUT = 30.0
ASYNC_CHECK_INTERVAL = 5.0


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-hqb2mp^(%q&i985hk3h+byeck!as4h@6@v+2ap0wqpw^w6_zl&'


# SECURITY WARNING: don't run with debug turned on in production!
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "formatters" : {
        "simple" : {
            "format" : "{levelname} {module} {asctime} - {message}",
            "style" : "{"
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            "formatter" : "simple"
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    "loggers" : {
        'django': {
            'handlers': ['console'],
            'propagate': False,
        },
        'renderers': {
            'handlers': ['console'],
            'propagate': False,
        }
        
    }
}


ALLOWED_HOSTS = [HOSTNAME, IP]
PROTO = env("PROTO")
CSRF_TRUSTED_ORIGINS = ["{}://{}".format(PROTO, HOSTNAME), "{}://{}:{}".format(PROTO, HOSTNAME, PORT)]
USE_X_FORWARDED_HOST = HOSTNAME != "localhost"
DEBUG = env("DEBUG")
INTERNAL_IPS = [
    "127.0.0.1"
]


# Application definition
INSTALLED_APPS = [
    'django.contrib.sessions',    
    'django.contrib.contenttypes',
    'django.contrib.humanize.apps.HumanizeConfig',
    'django.contrib.admin',
    'django.contrib.auth',    
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'debug_toolbar',
    'mptt',
    'sekizai',
    'sorl.thumbnail',
    'pyochre.server.ochre',
    'wiki.apps.WikiConfig',
    'wiki.plugins.macros.apps.MacrosConfig',
    'wiki.plugins.images.apps.ImagesConfig',
    'wiki.plugins.attachments.apps.AttachmentsConfig'
] + (
    ['django.contrib.staticfiles'] #if HOSTNAME == "localhost" else []
) + [
    'rest_framework',
    'django_extensions',
    'guardian',
    'django_registration',
]


#CORS_ALLOW_ALL_ORIGINS = True


# NOTE: We use a slight customization of the default User model
# that Django provides.
AUTH_USER_MODEL = "ochre.User"
ACCOUNT_ACTIVATION_DAYS = 1
ANONYMOUS = True


SITE_ID = 1


WIKI_USE_BOOTSTRAP_SELECT_WIDGET= False
WIKI_ACCOUNT_HANDLING = False
WIKI_ACCOUNT_SIGNUP_ALLOWED = False
WIKI_EDITOR = "pyochre.server.ochre.fields.WikiMarkdownField"
WIKI_MARKDOWN_KWARGS = {
    'extensions': [
        'footnotes',
        'attr_list',
        'extra',
        'codehilite',
    ]
}


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'debug_toolbar.middleware.DebugToolbarMiddleware',    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


X_FRAME_OPTIONS = "SAMEORIGIN"

ROOT_URLCONF = 'pyochre.server.ochre.urls'

TEMPLATES = [
    {
        "NAME" : "primary",
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates/"],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pyochre.server.ochre.context_processors.app_directory',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                "sekizai.context_processors.sekizai",
            ],
            "loaders" : [
                (
                    'django.template.loaders.locmem.Loader',
                    template_dict
                ),
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.filesystem.Loader',
            ]            
        }
    },
]

WSGI_APPLICATION = 'pyochre.server.ochre.wsgi.application'

AUTHENTICATION_BACKENDS = (
    ["django_auth_ldap.backend.LDAPBackend"] if env("USE_LDAP") else []
) + [
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
]

# NOTE: These groups correspond to those who can use or work with the web
#       framework or workstations.
LDAP_WEB_GROUP = env("LDAP_WEB_GROUP")
LDAP_WEB_ADMIN_GROUP = env("LDAP_WEB_ADMIN_GROUP")
LDAP_WORKSTATION_GROUP = env("LDAP_WORKSTATION_GROUP")
LDAP_WORKSTATION_ADMIN_GROUP = env("LDAP_WORKSTATION_ADMIN_GROUP")

if USE_LDAP:
    import ldap
    from django_auth_ldap.config import LDAPSearch, PosixGroupType
    
    LDAP_ROOT_BASE_COMPONENTS = env("LDAP_ROOT_BASE_COMPONENTS")
    LDAP_USER_BASE_COMPONENTS = env("LDAP_USER_BASE_COMPONENTS")
    LDAP_GROUP_BASE_COMPONENTS = env("LDAP_GROUP_BASE_COMPONENTS")
    LDAP_ROOT_BASE = ",".join(LDAP_ROOT_BASE_COMPONENTS)
    LDAP_USER_BASE = ",".join(LDAP_USER_BASE_COMPONENTS + LDAP_ROOT_BASE_COMPONENTS)
    LDAP_GROUP_BASE = ",".join(LDAP_GROUP_BASE_COMPONENTS + LDAP_ROOT_BASE_COMPONENTS)

    LDAP_WEB_GROUP_DN = "cn={},{}".format(LDAP_WEB_GROUP, LDAP_GROUP_BASE)
    LDAP_WORKSTATION_GROUP_DN = "cn={},{}".format(LDAP_WORKSTATION_GROUP, LDAP_GROUP_BASE)
    LDAP_WEB_ADMIN_GROUP_DN = "cn={},{}".format(LDAP_WEB_ADMIN_GROUP, LDAP_GROUP_BASE)
    LDAP_WORKSTATION_ADMIN_GROUP_DN = "cn={},{}".format(LDAP_WORKSTATION_ADMIN_GROUP, LDAP_GROUP_BASE)
        
    AUTH_LDAP_START_TLS = not DEBUG
    if AUTH_LDAP_START_TLS:
        ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, str(DATA_DIR / "certs" / "ldap.pem"))
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
        ldap.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
        

    # NOTE:
    #
    #
    AUTH_LDAP_CERT_FILE = env("LDAP_CERT_FILE")
    AUTH_LDAP_SERVER_URI = env("LDAP_SERVER_URI")
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        LDAP_USER_BASE, ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
    )
    AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
        LDAP_GROUP_BASE, ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
    )
    AUTH_LDAP_GROUP_TYPE = PosixGroupType()
    AUTH_LDAP_FIND_GROUP_PERMS = True
    AUTH_LDAP_MIRROR_GROUPS = True
    AUTH_LDAP_ADMIN_CN = "admin"
    AUTH_LDAP_BIND_DN = "cn={},{}".format(AUTH_LDAP_ADMIN_CN, LDAP_ROOT_BASE)
    AUTH_LDAP_BIND_PASSWORD_FILE = env("AUTH_LDAP_BIND_PASSWORD_FILE")
    with open(AUTH_LDAP_BIND_PASSWORD_FILE, "rt") as ifd:
        AUTH_LDAP_BIND_PASSWORD = ifd.read()
    AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn", "email" : "mail"}

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST' : env("POSTGRES_HOST"),
        'NAME': env("POSTGRES_DB_NAME"),
        'USER': env("POSTGRES_USER"),
        'PASSWORD' : env("POSTGRES_PASSWORD"),
        "PORT" : env("POSTGRES_PORT")
    } if USE_POSTGRES else {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_DIR / 'db.sqlite3',
    }
}


# CACHEOPS_REDIS = {
#     'host': 'localhost', # redis-server is on same machine
#     'port': 6379,        # default redis port
#     'db': 3,             # SELECT non-default redis database
#                          # using separate redis db or redis instance
#                          # is highly recommended

#     #'socket_timeout': 3,   # connection timeout in seconds, optional
#     #'password': '...',     # optional
#     #'unix_socket_path': '' # replaces host and port
# }
# CACHEOPS_DEFAULTS = {
#     'timeout': 60*60
# }
# CACHEOPS = {
#     'auth.user': {'ops': 'get', 'timeout': 60*15},
#     'auth.*': {'ops': ('fetch', 'get')},
#     'auth.permission': {'ops': 'all'},
#     '*.*': {},
# }


CACHES = {
    #'default': {
    #    'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    #},
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'sessions_table',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}

USE_DEPRECATED_PYTZ = True

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_L10N = True
USE_TZ = True

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.template.context_processors.request"
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
