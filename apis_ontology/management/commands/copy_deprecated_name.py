from django.core.management.base import BaseCommand

from apis_ontology.models import Person, Function, Place, Institution, Event, Salary


class Command(BaseCommand):
    help = "copy values from deprecated_name to name"

    def handle(self, *args, **options):
        models = [Person, Function, Place, Institution, Event, Salary]
        for model in models:
            all_instances = model.objects.all()
            for instance in all_instances:
                instance.name = instance.deprecated_name
            res = model.objects.bulk_update(all_instances, fields=["name"], batch_size=1_000)
            print(f"Updated {res} {model} instances")
