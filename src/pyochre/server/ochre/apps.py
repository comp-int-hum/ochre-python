from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'pyochre.server.ochre'
    label = 'ochre'

    def ready(self):
        from . import signals
