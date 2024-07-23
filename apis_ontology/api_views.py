from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework import pagination
from apis_ontology.serializers import TempTripleSerializer
from apis_core.apis_relations.models import TempTriple
from apis_core.generic.api_views import ModelViewSet
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from apis_core.utils.helpers import get_content_types_with_allowed_relation_from
import time


class InjectFacetPagination(pagination.LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        start = time.time()
        self.facets = self.calculate_facets(queryset)
        print("Used " + str(time.time() - start) + "ms for calculating the facets")
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data.update(self.facets)
        response.data = dict(sorted(response.data.items()))
        return response

    def calculate_facets(self, queryset):
        facets = {"start": None,
                  "end": None,
                  "gender": {},
                  "type": {}}
        print("calculate_facets")
        for obj in queryset:
            for attribute in ["gender", "type"]:
                if hasattr(obj, attribute):
                    value = getattr(obj, attribute)
                    id = value or "emtpy"
                    facetdict = facets[attribute].get(id, {"name": value, "count": 0})
                    facetdict["count"] += 1
                    facets[attribute][id] = facetdict
                else:
                    facets.pop(attribute, None)
            if start_date := getattr(obj, "start_date", None):
                facets["start"] = min(start_date.year, facets["start"], key=lambda x: x or 1600)
            if end_date := getattr(obj, "end_date", None):
                facets["end"] = max(end_date.year, facets["end"], key=lambda x: x or 1300)

        content_type = ContentType.objects.get_for_model(queryset.model)
        relation_content_types = get_content_types_with_allowed_relation_from(content_type)

        for relation_content_type in relation_content_types:
            facetname = "relation_" + relation_content_type.name
            facets[facetname] = {}
            model = relation_content_type.model_class()
            res = list(model.objects.filter(triple_set_from_subj__obj__in=queryset).distinct().annotate(count=Count("id")))
            res += list(model.objects.filter(triple_set_from_obj__subj__in=queryset).distinct().annotate(count=Count("id")))
            for obj in res:
                name = obj.name
                if relation_content_type.name == "person":
                    name = f"{obj.first_name} {obj.name}"
                if obj.id in facets[facetname].keys():
                    facets[facetname][obj.id]["count"] += obj.count
                else:
                    facets[facetname][obj.id] = {"name": name, "count": obj.count}
        print("end calculate facets")
        return {"facets": facets}


class ListEntityRelations(ListAPIView):
    serializer_class = TempTripleSerializer

    def get_queryset(self):
        contenttype = self.kwargs["contenttype"]
        pk = self.kwargs["pk"]
        obj = get_object_or_404(contenttype.model_class(), pk=pk)
        return TempTriple.objects.filter(Q(subj=obj)|Q(obj=obj)).prefetch_related("subj", "obj", "prop")

    def get_serializer_context(self):
        contenttype = self.kwargs["contenttype"]
        pk = self.kwargs["pk"]
        context = super().get_serializer_context()
        context["obj"] = get_object_or_404(contenttype.model_class(), pk=pk)
        return context


class SicprodModelViewSet(ModelViewSet):
    """
    We override the generic ModelViewSet so we can add the facet
    information to the -list output
    """

    pagination_class = InjectFacetPagination
