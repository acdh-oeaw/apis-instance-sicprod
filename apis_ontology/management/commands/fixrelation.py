from django.core.management.base import BaseCommand

from apis_core.apis_entities.models import TempEntityClass
from apis_core.apis_metainfo.models import Collection
from apis_core.apis_relations.models import TempTriple, Property

from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Combine parent relations (142 should be 144 and subj/obj interchanged)"

    def handle(self, *args, **options):
        r142 = TempTriple.objects.filter(prop=142)
        print(len(r142))

        for tt in r142:
            print(tt)
            obj = tt.obj
            subj = tt.subj
            tt.obj = subj
            tt.subj = obj
            tt.prop = Property.objects.get(pk=144)
            print(tt)
            tt.save()

        r142 = TempTriple.objects.filter(prop=142)
        print(len(r142))

