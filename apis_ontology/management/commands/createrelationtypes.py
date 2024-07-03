import json
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import properties from data/properties.json"

    def handle(self, *args, **options):
        base_path = Path(__file__).resolve().parent.parent.parent.parent
        properties_json = base_path / "data/properties.json"
        data = json.loads(properties_json.read_text())

        for p in data:
            classname = p["name"].replace(" ", "_").capitalize()
            subj_models = ", ".join(p["subj"])
            obj_models = ", ".join(p["obj"])
            print(f"class {classname}(Relation):")
            print("    class Meta:")
            print(f"        verbose_name = \"{p['name']}\"")
            print(f"    subj_model = {subj_models}")
            print(f"    obj_model = {obj_models}\n\n")
