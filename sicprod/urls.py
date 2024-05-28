from apis_acdhch_default_settings.urls import urlpatterns
from django.urls import path, include
from rest_framework import routers

from apis_ontology.api_views import ListEntityRelations, SicprodModelViewSet

urlpatterns += [path("", include("django_acdhch_functions.urls")),]
urlpatterns += [path("logger/", include("django_action_logger.urls")),]

urlpatterns += [path("apis/api/<contenttype:contenttype>/<int:pk>/relations", ListEntityRelations.as_view(), name="relationslist")]

# We override the generic ModelViewSet URIs using a custom ModelViewSet
# so we can add the faceting information to the `list` response
router = routers.DefaultRouter()
router.register(r"", SicprodModelViewSet, basename="genericmodelapi")
urlpatterns.insert(0, path("apis/api/<contenttype:contenttype>/", include(router.urls)))
