import requests
import os

from django.core.management.base import BaseCommand
from apis_ontology.models import Event, Function, Institution, Person, Place, Salary
from apis_core.apis_metainfo.models import Uri, RootObject

from apis_core.utils import caching

TOKEN = os.environ.get("TOKEN")
HEADERS = {"Authorization": f"Token {TOKEN}"}

SRC = "https://sicprod.acdh-dev.oeaw.ac.at/apis/api"

def import_uris():
    nextpage = f"{SRC}/metainfo/uri/?format=json&limit=1000"
    while nextpage:
        print(nextpage)
        page = requests.get(nextpage, headers=HEADERS)
        data = page.json()
        nextpage = data['next']
        for result in data["results"]:
            print(result["url"])
            try:
                newuri, created = Uri.objects.get_or_create(id=result["id"], uri=result["uri"])
            except utils.IntegrityError:
                print(f"IntegrityError: {result['id']}")
            del result["uri"]
            del result["id"]
            if result["entity"] and "id" in result["entity"]:
                try:
                    result["root_object"] = RootObject.objects.get(pk=result["entity"]["id"])
                except RootObject.DoesNotExist:
                    result["root_object"] = None
                    print(f"RootObject with ID {result['entity']['id']} not found")
            else:
                print(f"No entity.id set for URI: {result}")
            for attribute in result:
                if hasattr(newuri, attribute):
                    setattr(newuri, attribute, result[attribute])
            newuri.save()


def import_entities():
    entities_classes = caching.get_all_entity_classes() or []

    for entity in entities_classes:
        nextpage = f"{SRC}/ontology/{entity.__name__.lower()}/?format=json&limit=500"
        while nextpage:
            print(nextpage)
            page = requests.get(nextpage, headers=HEADERS)
            data = page.json()
            nextpage = data['next']
            for result in data["results"]:
                result_id = result["id"]
                newentity, created = entity.objects.get_or_create(pk=result_id)
                del result["self_contenttype"]
                for attribute in result:
                    if hasattr(newentity, attribute):
                        setattr(newentity, attribute, result[attribute])
                newentity.save()


class Command(BaseCommand):
    help = "Import wikidata coordinates from places with wikidata links"

    def handle(self, *args, **options):
        import_entities()
        #import_uris()
