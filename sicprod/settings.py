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
INSTALLED_APPS += ["apis_core.collections"]
INSTALLED_APPS += ["apis_core.history"]
INSTALLED_APPS += ["simple_history"]
INSTALLED_APPS += ["auditlog"]
INSTALLED_APPS += ["django_grouper"]
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
    if view.permission_action_required == "view":
        obj = view.get_object()
        from apis_core.collections.models import SkosCollectionContentObject
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(obj)
        return SkosCollectionContentObject.objects.filter(content_type=ct, object_id=obj.id, collection__name="published").exists()
    return False


# we have to set this, otherwise there is an error
APIS_DETAIL_VIEWS_ALLOWED = True
APIS_VIEW_PASSES_TEST = apis_view_passes_test


def apis_list_view_object_filter(view, queryset):
    if view.request.user.is_authenticated:
        return queryset
    from apis_core.collections.models import SkosCollectionContentObject
    from django.contrib.contenttypes.models import ContentType
    ct = ContentType.objects.get_for_model(queryset.model)
    sccos = SkosCollectionContentObject.objects.filter(content_type=ct, collection__name="published").values_list("object_id")
    return queryset.filter(pk__in=sccos)


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

APIS_ENTITIES = {
        "Event": {"relations_per_page": 1000},
        "Function": {"relations_per_page": 1000},
        "Institution": {"relations_per_page": 1000},
        "Person": {"relations_per_page": 1000},
        "Place": {"relations_per_page": 1000},
        "Salary": {"relations_per_page": 1000},
        }

INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"] + MIDDLEWARE
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "https://sicprod-frontend.acdh-ch-dev.oeaw.ac.at", "https://sicprod.acdh.oeaw.ac.at"]

SPECTACULAR_SETTINGS["DEFAULT_GENERATOR_CLASS"] = 'apis_ontology.generators.SicprodCustomSchemaGenerator'

MIDDLEWARE += ['auditlog.middleware.AuditlogMiddleware']
