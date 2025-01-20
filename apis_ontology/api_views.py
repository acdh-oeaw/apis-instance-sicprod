import django_filters
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework import pagination
from apis_ontology.serializers import RelationSerializer, NetworkSerializer
from apis_core.generic.api_views import ModelViewSet
from django.contrib.contenttypes.models import ContentType
from apis_core.apis_metainfo.models import RootObject
from apis_core.apis_relations.models import Triple
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import OuterRef
from django.db.models import Case, When
from apis_ontology.filtersets import NetworkFilterSet
from apis_ontology.models import Salary
from apis_core.relations.models import Relation
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
                return f"{obj.first_name} {obj.name}"
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

        content_type = ContentType.objects.get_for_model(queryset.model)

        obj_rels = Relation.objects.filter(subj_content_type=content_type)
        subj_rels = Relation.objects.filter(obj_content_type=content_type)

        for relation in obj_rels:
            facetname = "relation_" + relation.obj_content_type.name
            if facetname not in facets:
                facets[facetname] = {}
            count = facets[facetname].get(relation.obj_object_id, {}).get("count", 0)
            facets[facetname][relation.obj_object_id] = {"name": self.get_pretty_object_name(relation.obj), "count": count+1}
        for relation in subj_rels:
            facetname = "relation_" + relation.subj_content_type.name
            if facetname not in facets:
                facets[facetname] = {}
            count = facets[facetname].get(relation.subj_object_id, {}).get("count", 0)
            facets[facetname][relation.subj_object_id] = {"name": self.get_pretty_object_name(relation.subj), "count": count+1}

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


class Network(ListAPIView):
    serializer_class = NetworkSerializer
    filterset_class = NetworkFilterSet
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def get_queryset(self):
        relation_subquery = Triple.objects.filter(Q(subj=OuterRef("pk"))|Q(obj=OuterRef("pk"))).annotate(
                other_id=Case(
                    When(subj=OuterRef("pk"), then="obj"),
                    default="subj")).values("other_id")
        return RootObject.objects_inheritance.select_subclasses().annotate(related_to=ArraySubquery(relation_subquery)).distinct()
