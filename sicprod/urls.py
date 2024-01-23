from apis_acdhch_default_settings.urls import urlpatterns
from django.urls import path, include
from apis_ontology.views import CustomReferenceDetailView, TempTripleAutocomplete, CustomReferenceDeleteView
from django.contrib.auth.decorators import login_required

customurlpatterns = [
    path("bibsonomy/references/<int:pk>", login_required(CustomReferenceDetailView.as_view()), name='referencedetail'),
    path('bibsonomy/temptriple-autocomplete/', TempTripleAutocomplete.as_view(), name="temptriple-autocomplete",),
    path('bibsonomy/references/<int:pk>/delete', login_required(CustomReferenceDeleteView.as_view()), name='referencedelete'),
]
urlpatterns += [path("", include("django_acdhch_functions.urls")),]
urlpatterns = customurlpatterns + urlpatterns
