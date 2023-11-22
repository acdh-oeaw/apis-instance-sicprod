from django.apps import AppConfig


class ApisOntologyConfig(AppConfig):
    name = 'apis_ontology'

    def ready(self):
        from . import signals
