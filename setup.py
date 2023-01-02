from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = f.read()

setup(
    name='pyochre',
    version='0.0.4',
    description='Client and server for the Open Computational Humanities Research Ecosystem (OCHRE)',
    long_description=long_description,
    author='Tom Lippincott',
    author_email='tom.lippincott@jhu.edu',
    url='https://github.com/comp-int-hum/ochre-python',
    packages=[
        "pyochre",
        "pyochre.utils",
        "pyochre.rest",
        "pyochre.primary_sources",
        "pyochre.machine_learning",
        "pyochre.scholarly_knowledge",
        "pyochre.server",
        "pyochre.server.ochre",
    ] + [
        "pyochre.server.ochre.{}".format(x) for x in [
            "content_negotiation",
            "context_processors",
            "decorators",
            "fields",
            "forms",
            "models",
            "migrations",            
            "models",
            "parsers",
            "renderers",
            "routers",
            "serializers",
            "signals",
            "templatetags",
            "urls",
            "vega",
            "views",
            "viewsets",
            "widgets"
        ]
    ],
    install_requires=[
        "captum",
        "celery",
        "django",
        "djangorestframework",
        "django-cors-headers",
        "django-debug-toolbar",
        "django-environ",
        "django-extensions",
        "django-guardian",
        "django-mptt",
        "django-registration",
        "django-sekizai",
        "drf-nested-routers",
        "gensim",
        "jsonpath-python",
        "jsonpath_ng",
        "pairtree",
        "python-dotenv",
        "rdflib",
        "redis",
        "requests",
        "spacy",
        "torch",
        "torchvision",
        "torch-model-archiver",
        "transformers",
        "watchdog",
        "wiki",
        "wikidata",
    ],
    extras_require={
        "ldap" : [
            "django-auth-ldap",
            "python-ldap"
        ],
        "postgres" : [
            "psycopg2"
        ],
        "torchserve" : [
            "torchserve"
        ]
    },
    include_package_data=True
)
