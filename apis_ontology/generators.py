from apis_core.generic.generators import CustomEndpointEnumerator
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from drf_spectacular.generators import SchemaGenerator

from apis_core.apis_entities.models import AbstractEntity
from apis_ontology.api_views import ListEntityRelations


class SicprodCustomEndpointEnumerator(CustomEndpointEnumerator):
    # We override the APIS CustomEndpointEnumerator so we can
    # add our custom `relations` endpoints

    def _generate_relations_endpoints(self, content_type: ContentType):
        path = reverse("relationslist", args=[content_type, 0])
        path = path.replace("0", "{id}")
        regex = path
        callback = ListEntityRelations(contenttype=content_type).as_view()
        return (path, regex, "GET", callback)

    def get_api_endpoints(self, patterns=None, prefix=""):
        api_endpoints = super().get_api_endpoints(patterns, prefix)
        for content_type in ContentType.objects.all():
            if content_type.model_class() is not None and issubclass(
                content_type.model_class(), AbstractEntity
            ):
                api_endpoints.append(self._generate_relations_endpoints(content_type))
        return api_endpoints


class SicprodCustomSchemaGenerator(SchemaGenerator):
    endpoint_inspector_cls = SicprodCustomEndpointEnumerator
