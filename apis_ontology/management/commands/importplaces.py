import pathlib
import re
import time

from django.core.management.base import BaseCommand
from apis_core.utils import rdf

from apis_ontology.models import Place


class Command(BaseCommand):
    help = "Import wikidata coordinates from places with wikidata links"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=pathlib.Path)

    def handle(self, *args, **options):
        pattern = re.compile("http[s]?://www.wikidata.org/wiki/(?P<wikidataid>.+)")
        configfile = options["file"]

        for p in Place.objects.all(): #[Place.objects.first()]:
            if res := re.search(pattern, p.references):
                print(p)
                uri = f"https://www.wikidata.org/wiki/Special:EntityData/{res.group(1)}.rdf?flavor=simple"
                try:
                    model, data = rdf.get_modelname_and_dict_from_uri(uri, configfile)
                    if not p.longitude:
                        p.longitude = data['longitude']
                    else:
                        print(f"Longitude already set for {p}")
                    if not p.latitude:
                        p.latitude = data['latitude']
                    else:
                        print(f"Latitude already set for {p}")
                    p.save()
                except Exception:
                    print(f"not found {p}")
                    pass
                time.sleep(1)
