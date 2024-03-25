from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apis_core.apis_metainfo.models import Collection
from apis_core.collections.models import SkosCollection, SkosCollectionContentObject


class Command(BaseCommand):
    help = "migrate from apis_metainfo.collection to collections.skoscollection"

    def handle(self, *args, **options):
        sets = ["person_set", "function_set", "place_set", "institution_set", "event_set", "salary_set"]
        parentskoscol, _ = SkosCollection.objects.get_or_create(name="sicprod")
        for col in Collection.objects.all():
            print(col)
            skoscol, _ = SkosCollection.objects.get_or_create(name=col.name, parent=parentskoscol)
            for s in sets:
                entity_set = getattr(col, s)
                for entity in entity_set.all():
                    ct = ContentType.objects.get_for_model(entity)
                    scco, _ = SkosCollectionContentObject.objects.get_or_create(collection=skoscol, content_type=ct, object_id=entity.id)
                    print(scco)
