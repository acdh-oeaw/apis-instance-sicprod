from apis_acdhch_default_settings.urls import urlpatterns
from django.urls import path, include

from apis_ontology.api_views import ListEntityRelations

urlpatterns += [path("", include("django_acdhch_functions.urls")),]
urlpatterns += [path("logger/", include("django_action_logger.urls")),]

urlpatterns += [path("apis/api/<contenttype:contenttype>/<int:pk>/relations", ListEntityRelations.as_view(), name="relationslist")]
