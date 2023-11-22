import requests
import os

from django.db import utils
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from apis_ontology.models import Event, Function, Institution, Person, Place, Salary
from apis_core.apis_metainfo.models import Uri, RootObject, Collection
from apis_bibsonomy.models import Reference
from apis_core.apis_relations.models import Property, TempTriple

from apis_core.utils import caching

TOKEN = os.environ.get("TOKEN")
HEADERS = {"Authorization": f"Token {TOKEN}"}

SRC = "https://sicprod.acdh-dev.oeaw.ac.at/apis/api"


def import_labels():
    nextpage = f"https://sicprod.acdh-dev.oeaw.ac.at/custom/api/labels/?format=json&limit=1000"
    while nextpage:
        print(nextpage)
        page = requests.get(nextpage, headers=HEADERS)
        data = page.json()
        nextpage = data['next']
        for result in data["results"]:
            ltype = result["label_type"]["name"]
            entity = RootObject.objects_inheritance.get_subclass(id=result["temp_entity"]["id"])
            md = entity.metadata or {}
            if ltype in md:
                md[ltype].append(result["label"])
            else:
                md[ltype] = [result["label"]]
            entity.metadata = md
            entity.save()


def import_bibsonomy():
    nextpage = f"https://sicprod.acdh-dev.oeaw.ac.at/custom/api/references/?format=json&limit=1000"
    while nextpage:
        print(nextpage)
        page = requests.get(nextpage, headers=HEADERS)
        data = page.json()
        nextpage = data['next']
        for result in data["results"]:
            if "content_type" in result:
                ct = ContentType.objects.get_by_natural_key(result["content_type"]["app_label"], result["content_type"]["model"])
            del result["content_type"]
            ref, created = Reference.objects.get_or_create(id=result["id"], bibs_url=result["bibs_url"], object_id=result["object_id"], content_type_id=ct.pk, bibtex=result["bibtex"])
            for attribute in result:
                if hasattr(ref, attribute):
                    setattr(ref, attribute, result[attribute])
            ref.save()


def import_uris():
    nextpage = f"{SRC}/metainfo/uri/?format=json&limit=1000"
    while nextpage:
        print(nextpage)
        page = requests.get(nextpage, headers=HEADERS)
        data = page.json()
        nextpage = data['next']
        for result in data["results"]:
            try:
                newuri, created = Uri.objects.get_or_create(id=result["id"])
            except utils.IntegrityError:
                print(f"IntegrityError: {result['id']}")
            if result["root_object"] and "id" in result["root_object"]:
                try:
                    newuri.root_object = RootObject.objects.get(pk=result["root_object"]["id"])
                except RootObject.DoesNotExist:
                    print(f"RootObject {result['root_object']['id']} does not exist")
            else:
                print(f"No entity.id set for URI: {result}")
            del result["id"]
            del result["root_object"]
            for attribute in result:
                if hasattr(newuri, attribute):
                    setattr(newuri, attribute, result[attribute])
            newuri.save()


def import_collections():
    page = f"{SRC}/metainfo/collection/"

    page = requests.get(page, headers=HEADERS)
    data = page.json()
    for result in data["results"]:
        result_id = result["id"]
        newcol, created = Collection.objects.get_or_create(pk=result_id)
        for attribute in result:
            if hasattr(newcol, attribute):
                setattr(newcol, attribute, result[attribute])
        newcol.save()


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
                for collection in result["collection"]:
                    newentity.collection.add(Collection.objects.get(pk=collection["id"]))
                del result["collection"]
                for attribute in result:
                    if hasattr(newentity, attribute):
                        setattr(newentity, attribute, result[attribute])
                newentity.save()


def import_properties():
    page = f"{SRC}/relations/property/"

    page = requests.get(page, headers=HEADERS)
    data = page.json()
    for result in data["results"]:
        result_id = result["id"]
        newprop, created = Property.objects.get_or_create(pk=result_id)
        del result["self_contenttype"]
        for subjclass in result["subj_class"]:
            subjlabel, subjmodel = subjclass["label"].split("|")
            if subjmodel.strip() != "court":
                newprop.subj_class.add(ContentType.objects.get_by_natural_key(subjlabel.strip(), subjmodel.strip()))
        for objclass in result["obj_class"]:
            objlabel, objmodel = objclass["label"].split("|")
            if objmodel.strip() != "court":
                newprop.obj_class.add(ContentType.objects.get_by_natural_key(objlabel.strip(), objmodel.strip()))
        del result["subj_class"]
        del result["obj_class"]
        for attribute in result:
            if hasattr(newprop, attribute):
                setattr(newprop, attribute, result[attribute])
        newprop.save()


def import_temptriple():
    nextpage = f"{SRC}/relations/temptriple/?format=json&limit=500"
    while nextpage:
        print(nextpage)
        page = requests.get(nextpage, headers=HEADERS)
        data = page.json()
        nextpage = data['next']
        for result in data["results"]:
            result_id = result["id"]
            subj = RootObject.objects_inheritance.get_subclass(pk=result["subj"]["id"])
            obj = RootObject.objects_inheritance.get_subclass(pk=result["obj"]["id"])
            prop = Property.objects.get(pk=result["prop"]["id"])
            newtt, created = TempTriple.objects.get_or_create(pk=result_id, subj=subj, obj=obj, prop=prop)
            del result["subj"]
            del result["obj"]
            del result["prop"]
            for attribute in result:
                if hasattr(newtt, attribute):
                    setattr(newtt, attribute, result[attribute])
            newtt.save()


class Command(BaseCommand):
    help = "Import from old sicprod instance"

    def handle(self, *args, **options):
        import_collections()
        import_entities()
        import_uris()
        import_bibsonomy()
        import_labels()
        import_properties()
        import_temptriple()
