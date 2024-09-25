from django.core.management.base import BaseCommand
import json
import pathlib
import requests


class Command(BaseCommand):
    help = "Update iiif cache"

    def handle(self, *args, **options):
        full_dict = {}
        try:
            titles = requests.get("https://iiif.acdh-dev.oeaw.ac.at/images/sicprod/", headers={"Accept": "application/json"})
            for title in titles.json():
                full_dict[title] = requests.get(f"https://iiif.acdh-dev.oeaw.ac.at/images/sicprod/{title}", headers={"Accept": "application/json"}).json()
        except Exception as e:
            print(e)
        pathlib.Path("data/iiif.json").write_text((json.dumps(full_dict, indent=2)))
