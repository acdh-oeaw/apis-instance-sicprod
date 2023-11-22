from django.core.management.base import BaseCommand

from apis_core.apis_entities.models import TempEntityClass
from apis_core.apis_metainfo.models import Collection

from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Add all entities to `published` collection"

    def handle(self, *args, **options):
        published, _ = Collection.objects.get_or_create(name="published")

        for model in ContentType.objects.filter(app_label='apis_ontology'):
            if model.model_class():
                if issubclass(model.model_class(), TempEntityClass):
                    for entity in model.model_class().objects.all():
                        entity.collection.add(published)
