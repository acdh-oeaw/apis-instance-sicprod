from apis_acdhch_default_settings.settings import *
import re
import dj_database_url
import os


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
REDMINE_ID = "20870"
APIS_LIST_VIEWS_ALLOWED = False
APIS_DETAIL_VIEWS_ALLOWED = False
FEATURED_COLLECTION_NAME = "FEATURED"
# MAIN_TEXT_NAME = "ÖBL Haupttext"
BIRTH_REL_NAME = "geboren in"
DEATH_REL_NAME = "verstorben in"
APIS_LOCATED_IN_ATTR = ["located in"]
APIS_BASE_URI = "https://sicprod.acdh.oeaw.ac.at/"
# APIS_OEBL_BIO_COLLECTION = "ÖBL Biographie"

APIS_SKOSMOS = {
    "url": os.environ.get("APIS_SKOSMOS", "https://vocabs.acdh-dev.oeaw.ac.at"),
    "vocabs-name": os.environ.get("APIS_SKOSMOS_THESAURUS", "apisthesaurus"),
    "description": "Thesaurus of the APIS project. Used to type entities and relations.",
}

APIS_BIBSONOMY = [{
   'type': 'zotero', #or zotero
   'url': 'https://api.zotero.org', #url of the bibsonomy instance or zotero.org
   'user': os.environ.get('APIS_BIBSONOMY_USER'), #for zotero use the user id number found in settings
   'API key': os.environ.get('APIS_BIBSONOMY_PASSWORD'),
   'group': '4853010'
}]
APIS_BIBSONOMY_FIELDS = ['self']

DEBUG = True
DEV_VERSION = False

SPECTACULAR_SETTINGS["COMPONENT_SPLIT_REQUEST"] = True
SPECTACULAR_SETTINGS["COMPONENT_NO_READ_ONLY_REQUIRED"] = True

MAIN_TEXT_NAME = "ÖBL Haupttext"

LANGUAGE_CODE = "de"

INSTALLED_APPS += ["apis_bibsonomy"]
INSTALLED_APPS.remove("apis_ontology")
INSTALLED_APPS = ["apis_ontology"] + INSTALLED_APPS
INSTALLED_APPS = ["django_acdhch_functions"] + INSTALLED_APPS
PROJECT_METADATA = {
        "matomo_url": "https://matomo.acdh.oeaw.ac.at/",
        "matomo_id": 242
}

#STATICFILES_DIRS = [BASE_DIR + "/member_images"]

# APIS_COMPONENTS = ['deep learning']

# APIS_BLAZEGRAPH = ('https://blazegraph.herkules.arz.oeaw.ac.at/metaphactory-play/sparql', 'metaphactory-play', 'KQCsD24treDY')


APIS_RELATIONS_FILTER_EXCLUDE += ["annotation", "annotation_set_relation"]

from apis_ontology.filters import name_first_name_alternative_name_filter, name_alternative_name_filter, filter_empty_string, filter_status
#INSTALLED_APPS.append("apis_highlighter")
def salarychoices():
    from apis_ontology.models import Salary
    return Salary.TYP_CHOICES + (("empty", "Nicht gesetzt"),)

def placechoices():
    from apis_ontology.models import Place
    return Place.TYPE_CHOICES + (("empty", "Nicht gesetzt"),)

def genderchoices():
    from apis_ontology.models import Person
    return Person.GENDER_CHOICES + (("empty", "Nicht gesetzt"),)

detail_view_exclude = ["references", "notes", "published", "review"]

APIS_ENTITIES = {
    "Salary": {
        "relations_per_page": 100,
        "search": ["name"],
        "list_filters": {
            "typ": {"method": filter_empty_string, "extra": {"choices": salarychoices, "required": False }},
        },
        "detail_view_exclude": detail_view_exclude,

    },
    "Function": {
        "relations_per_page": 100,
        "search": ["name", "alternative_label"],
        "list_filters": {
            "name": {"method": name_alternative_name_filter, "label": "Name or alternative name"},
        },
        "table_fields": [
            "name",
            "alternative_label",
        ],
        "detail_view_exclude": detail_view_exclude,
    },
    "Court": {
        "relations_per_page": 100,
        "search": ["name", "alternative_label"],
        "detail_view_exclude": detail_view_exclude,
    },
    "Place": {
        "relations_per_page": 100,
        "merge": True,
        "search": ["name", "alternative_label"],
        "form_order": ["name", "kind", "lat", "lng", "status", "collection"],
        "table_fields": ["name"],
        "additional_cols": ["id", "lat", "lng", "part_of"],
        "list_filters": {
            "type": {"method": filter_empty_string, "extra": {"choices": placechoices, "required": False }},
        },
        "detail_view_exclude": detail_view_exclude,
    },
    "Person": {
        "relations_per_page": 100,
        "merge": True,
        "search": ["name", "first_name", "alternative_label"],
        "form_order": [
            "first_name",
            "name",
            "start_date_written",
            "end_date_written",
            "status",
            "collection",
        ],
        "table_fields": [
            "name",
            "first_name",
            "start_date_written",
            "end_date_written",
            "alternative_label",
            "status",
        ],
        "additional_cols": ["id", "gender"],
        "list_filters": {
            "name": {"method": name_first_name_alternative_name_filter, "label": "Name or first name or alternative name"},
            "gender": {"method": filter_empty_string, "extra": {"choices": genderchoices, "required": False}},
            "status": {"method": filter_status},
        },
        "detail_view_exclude": detail_view_exclude,
    },
    "Institution": {
        "relations_per_page": 100,
        "merge": True,
        "search": ["name", "alternative_label"],
        "form_order": [
            "name",
            "start_date_written",
            "end_date_written",
            "kind",
            "status",
            "collection",
        ],
        "additional_cols": [
            "id",
            "kind",
        ],
        "list_filters": {
            "name": {"method": name_alternative_name_filter},
        },
        "detail_view_exclude": detail_view_exclude,
    },
    "Work": {
        "relations_per_page": 100,
        "merge": True,
        "search": ["name"],
        "additional_cols": [
            "id",
            "kind",
        ],
        "detail_view_exclude": detail_view_exclude,
    },
    "Event": {
        "relations_per_page": 100,
        "merge": True,
        "search": ["name", "alternative_label"],
        "additional_cols": [
            "id",
        ],
        "detail_view_exclude": detail_view_exclude,
    },
}


BIBSONOMY_REFERENCE_SIMILARITY = ['bibs_url', 'pages_start', 'pages_end', 'folio']
ROOT_URLCONF = "sicprod.urls"


#####################
# Permission setup: #
#####################
def apis_view_passes_test(view) -> bool:
    if view.request.user.is_authenticated:
        return True
    obj = view.instance
    if hasattr(obj, 'collection'):
        return bool(obj.collection.filter(name="published"))
    return False


# we have to set this, otherwise there is an error
APIS_DETAIL_VIEWS_ALLOWED = True
APIS_VIEW_PASSES_TEST = apis_view_passes_test


def apis_list_view_object_filter(view, queryset):
    if view.request.user.is_authenticated:
        return queryset
    if hasattr(queryset.model, 'collection'):
        return queryset.filter(collection__name__contains="published")
    #TODO: this should filter all the other models that do not
    # have a collection attached!
    return queryset


APIS_LIST_VIEWS_ALLOWED = True
APIS_LIST_VIEW_OBJECT_FILTER = apis_list_view_object_filter

REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = ['rest_framework.permissions.IsAuthenticatedOrReadOnly']
