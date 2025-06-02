import django_filters
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import ListAPIView
from rest_framework import pagination
from apis_ontology.serializers import RelationSerializer, NetworkSerializer
from apis_core.generic.api_views import ModelViewSet
from apis_core.apis_metainfo.models import RootObject
from apis_ontology.filtersets import NetworkFilterSet
from apis_ontology.models import Salary
from apis_core.relations.models import Relation
from apis_core.relations.templatetags.relations import get_relation_targets_from
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

    def get_pretty_object_name(self, obj: object) -> str:
        match type(obj).__name__:
            case "Person":
                if obj.first_name:
                    return f"{obj.first_name} {obj.name}"
                return f"{obj.name}"
            case "Place":
                return obj.label
            case _:
                return getattr(obj, "name", None)

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

        targets = get_relation_targets_from(queryset.first())

        for ct in targets:
            facetname = "relation_" + ct.name
            facets[facetname] = {}
            rels_fwd = Relation.objects.filter(obj_content_type=ct.id, subj_object_id__in=queryset).annotate(f=F("subj_object_id"), t=F("obj_object_id")).values("t", "f")
            rels_bkw = Relation.objects.filter(subj_content_type=ct.id, obj_object_id__in=queryset).annotate(f=F("obj_object_id"), t=F("subj_object_id")).values("t", "f")
            rels = rels_fwd | rels_bkw
            related_ids = [x["t"] for x in rels]
            instances = ct.model_class().objects.filter(pk__in=related_ids)

            for obj in instances:
                related_ids = [x["f"] for x in rels if x["t"] == obj.id]
                name = self.get_pretty_object_name(obj)
                facets[facetname][obj.id] = {"name": name, "count": len(set(related_ids))}

        for facet in facets.keys():
            if facet.startswith("relation_"):
                facets[facet] = dict(sorted(facets[facet].items()))

        print("end calculate facets")
        return {"facets": facets}


class ListEntityRelations(ListAPIView):
    serializer_class = RelationSerializer

    def get_queryset(self):
        contenttype = self.kwargs["contenttype"]
        pk = self.kwargs["pk"]
        exclude_salaries = Salary.objects.exclude(typ__in=["Sold", "Provision", "Sonstiges"])
        return Relation.objects.filter(Q(subj_content_type=contenttype, subj_object_id=pk)|Q(obj_content_type=contenttype, obj_object_id=pk)).exclude(Q(subj_object_id__in=exclude_salaries)|Q(obj_object_id__in=exclude_salaries)).select_subclasses()

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

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, contenttype, format=None):
        return super().list(request, contenttype, format)


class Network(ListAPIView):
    serializer_class = NetworkSerializer
    filterset_class = NetworkFilterSet
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def get_queryset(self):
        return RootObject.objects_inheritance.select_subclasses().distinct()
