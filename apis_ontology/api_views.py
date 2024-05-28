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
    facet_attributes = ["gender", "type"]

    def generate_facet_data(self):
        facets = {}
        for el in self.filter_queryset(self.get_queryset()):
            for attribute in self.facet_attributes:
                val = getattr(el, attribute, None)
                if val is not None:
                    facets[attribute] = facets.get(attribute, {})
                    facets[attribute][val] = facets[attribute].get(val, 0) + 1
        return {"facets": facets}

    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        res.data.update(self.generate_facet_data())
        res.data = dict(sorted(res.data.items()))
        return res
