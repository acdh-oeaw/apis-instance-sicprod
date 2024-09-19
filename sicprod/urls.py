from apis_acdhch_default_settings.urls import urlpatterns
from django.urls import path, include
from rest_framework import routers

from apis_ontology.api_views import ListEntityRelations, SicprodModelViewSet, Network
from apis_ontology.views import UserAuditLog, ReferenceScanFail

urlpatterns += [path("", include("django_acdhch_functions.urls")),]

urlpatterns += [path("apis/api/<contenttype:contenttype>/<int:pk>/relations", ListEntityRelations.as_view(), name="relationslist")]

# We override the generic ModelViewSet URIs using a custom ModelViewSet
# so we can add the faceting information to the `list` response
router = routers.DefaultRouter()
router.register(r"", SicprodModelViewSet, basename="genericmodelapi")
urlpatterns.insert(0, path("apis/api/<contenttype:contenttype>/", include(router.urls)))

urlpatterns += [path("auditlog", UserAuditLog.as_view()),]

urlpatterns += [path("apis/api/network", Network.as_view(), name="network")]

urlpatterns += [path("apis/failingreferences", ReferenceScanFail.as_view(), name="referencescanfail")]

urlpatterns += [path("", include("django_grouper.urls"))]
