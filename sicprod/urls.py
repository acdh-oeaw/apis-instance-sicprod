from apis_acdhch_default_settings.urls import urlpatterns
from django.urls import path, include

urlpatterns += [path("", include("django_acdhch_functions.urls")),]
urlpatterns += [path("logger/", include("django_action_logger.urls")),]
