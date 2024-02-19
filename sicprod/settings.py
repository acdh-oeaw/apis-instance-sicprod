from apis_acdhch_default_settings.settings import *
import os


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
APIS_BASE_URI = "https://sicprod.acdh.oeaw.ac.at/"

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

LANGUAGE_CODE = "de"

INSTALLED_APPS += ["apis_bibsonomy"]
INSTALLED_APPS.remove("apis_ontology")
INSTALLED_APPS = ["apis_ontology"] + INSTALLED_APPS
INSTALLED_APPS = ["django_acdhch_functions"] + INSTALLED_APPS
INSTALLED_APPS += ["django_action_logger"]
PROJECT_METADATA = {
        "matomo_url": "https://matomo.acdh.oeaw.ac.at/",
        "matomo_id": 242
}

BIBSONOMY_REFERENCE_SIMILARITY = ['bibs_url', 'pages_start', 'pages_end', 'folio']
ROOT_URLCONF = "sicprod.urls"


#####################
# Permission setup: #
#####################
def apis_view_passes_test(view) -> bool:
    if view.request.user.is_authenticated:
        return True
    obj = view.get_object()
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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
       'verbose': {
           'format': '%(asctime)s %(name)-6s %(levelname)-8s %(message)s',
       },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

LOG_LIST_NOSTAFF_EXCLUDE_APP_LABELS = ["reversion", "admin", "sessions", "auth"]
