from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from apis_ontology.serializers import TempTripleSerializer
from apis_core.apis_relations.models import TempTriple
from apis_core.generic.api_views import ModelViewSet


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
    facet_attributes = ["gender", "type", "related_persons", "related_functions", "related_places", "related_institutions", "related_events", "related_salaries"]

    def generate_facet_data(self):
        facets = {"start": None, "end": None}
        for el in self.filter_queryset(self.get_queryset()):
            for attribute in self.facet_attributes:
                values = getattr(el, attribute, [])
                if isinstance(values, str):
                    values = [values]
                if values == None:
                    values = []

                for value in values:
                    facets[attribute] = facets.get(attribute, {})
                    match value:
                        case dict():
                            facetdict = facets[attribute].get(value["id"], {"name": value["name"], "count": 0 })
                            facetdict["count"] += 1
                            facets[attribute][value["id"]] = facetdict
                        case str():
                            id = value or "emtpy"
                            facetdict = facets[attribute].get(id, {"name": value, "count": 0})
                            facetdict["count"] += 1
                            facets[attribute][id] = facetdict
                        case None:
                            pass
                        case other:
                            print(f"Unusable value for facetlist: {other}")
            if start_date := getattr(el, "start_date", None):
                facets["start"] = min(start_date.year, facets["start"], key=lambda x: x or 1600)
            if end_date := getattr(el, "end_date", None):
                facets["end"] = max(end_date.year, facets["end"], key=lambda x: x or 1300)
        return {"facets": facets}

    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        res.data.update(self.generate_facet_data())
        res.data = dict(sorted(res.data.items()))
        return res
