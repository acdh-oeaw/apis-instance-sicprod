from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from apis_ontology.serializers import TempTripleSerializer
from apis_core.apis_relations.models import TempTriple


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
