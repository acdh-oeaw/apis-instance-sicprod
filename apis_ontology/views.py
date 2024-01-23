from apis_bibsonomy.views import ReferenceDetailView, ReferenceDeleteView
from django.contrib.contenttypes.models import ContentType
from apis_core.apis_relations.models import TempTriple
from apis_bibsonomy.models import Reference
from django.shortcuts import redirect
from django.urls import reverse
from django import forms
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from dal import autocomplete
from django.db.models import Q


class TempTripleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = TempTriple.objects.all()
        if self.q:
            q = Q(subj__name__icontains=self.q) | Q(prop__name__icontains=self.q) | Q(obj__name__icontains=self.q)
            qs = qs.filter(q)
        return qs


class TempTripleReferenceForm(forms.Form):
    ReferenceToObject = forms.ModelChoiceField(
            TempTriple.objects.all(),
            widget=autocomplete.ModelSelect2(url='temptriple-autocomplete', attrs={'class': 'form-control'}),
            label="Add relation"
    )


class CustomReferenceDetailView(ReferenceDetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['temptripleform'] = TempTripleReferenceForm(prefix="temptriple")
        return context

    def post(self, request, *args, **kwargs):
        view = ReferenceFormView.as_view()
        return view(request, *args, **kwargs)


class ReferenceFormView(FormView, SingleObjectMixin):
    model = Reference

    def get_success_url(self):
        return reverse('referencedetail', kwargs=self.request.resolver_match.kwargs)

    def post(self, request, *args, **kwargs):
        form = None
        newref = self.get_object()
        newref.pk = None
        newref._state.adding = True
        if 'temptriple-ReferenceToObject' in request.POST:
            form = TempTripleReferenceForm(request.POST, prefix="temptriple")
            if form.is_valid():
                rto = form.cleaned_data['ReferenceToObject']
                subclass = TempTriple.objects_inheritance.get_subclass(id=rto.id)
                newref.content_type = ContentType.objects.get_for_model(subclass)
                newref.object_id = rto.id
                newref.save()
        else:
            print("form is not valid")
        return redirect(self.get_success_url())


class CustomReferenceDeleteView(ReferenceDeleteView):
    def delete(self, request, *args, **kwargs):
        resp = super().delete(request, *args, **kwargs)
        # we set the status code to 200 for HTMX requests, so they don't get redirected
        if "HX-Request" in request.headers:
            resp.status_code = 200
        return resp
