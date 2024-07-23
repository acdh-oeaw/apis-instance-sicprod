from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework import pagination
from apis_ontology.models import Person
from apis_ontology.serializers import TempTripleSerializer
from apis_core.apis_relations.models import TempTriple
from apis_core.generic.api_views import ModelViewSet
from django.db.models import OuterRef, Value, Count 
from django.db.models.functions import Concat


class InjectFacetPagination(pagination.LimitOffsetPagination):
    facet_attributes = [
        "facet_functions",
        "facet_places",
        "facet_institutions",
        "facet_events",
        "facet_salaries",
    ]

    def paginate_queryset(self, queryset, request, view=None):
        self.facets = self.calculate_facets(queryset)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data.update(self.facets)
        return response

    def calculate_facets(self, queryset):
        print("calculate_facets")
        person_facets = (
            Person.objects.filter(
                Q(triple_set_from_subj__obj__in=queryset)
                | Q(triple_set_from_obj__subj__in=queryset)
            )
            .annotate(count=Count("name"), label=Concat("name", Value(", ")))
            .values("label", "count")
        )
        # facets = {"start": None, "end": None}
        # for el in queryset.iterator():
        #     for attribute in self.facet_attributes:
        #         values = getattr(el, attribute, [])
        #         if isinstance(values, str):
        #             values = [values]
        #         if values == None:
        #             values = []

        #         for value in values:
        #             facets[attribute] = facets.get(attribute, {})
        #             match value:
        #                 case dict():
        #                     facetdict = facets[attribute].get(
        #                         value["id"], {"name": value["name"], "count": 0}
        #                     )
        #                     facetdict["count"] += 1
        #                     facets[attribute][value["id"]] = facetdict
        #                 case str():
        #                     id = value or "emtpy"
        #                     facetdict = facets[attribute].get(
        #                         id, {"name": value, "count": 0}
        #                     )
        #                     facetdict["count"] += 1
        #                     facets[attribute][id] = facetdict
        #                 case None:
        #                     pass
        #                 case other:
        #                     print(f"Unusable value for facetlist: {other}")
        #     # if start_date := getattr(el, "start_date", None):
        #     #     facets["start"] = min(start_date.year, facets["start"], key=lambda x: x or 1600)
        #     # if end_date := getattr(el, "end_date", None):
        #     #     facets["end"] = max(end_date.year, facets["end"], key=lambda x: x or 1300)
        print("calculated facets")
        return {"facets": {"facet_persons": list(person_facets)}}


class ListEntityRelations(ListAPIView):
    serializer_class = TempTripleSerializer

    def get_queryset(self):
        contenttype = self.kwargs["contenttype"]
        pk = self.kwargs["pk"]
        obj = get_object_or_404(contenttype.model_class(), pk=pk)
        return TempTriple.objects.filter(Q(subj=obj) | Q(obj=obj)).prefetch_related(
            "subj", "obj", "prop"
        )

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
