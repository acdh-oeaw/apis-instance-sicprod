import requests
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from auditlog.models import LogEntry
from apis_bibsonomy.models import Reference
from apis_ontology.serializers import iiif_titles, get_folio
from functools import cache


class UserAuditLog(LoginRequiredMixin, ListView):
    def get_queryset(self, *args, **kwargs):
        return LogEntry.objects.filter(actor=self.request.user)


def scanfolderexists(ref):
    normtitle = ref.bibtexjson["title"].replace(" ", "_").replace("(", "").replace(")", "")
    return normtitle in iiif_titles()


@cache
def iiif_files(title):
    files = requests.get(f"https://iiif.acdh-dev.oeaw.ac.at/images/sicprod/{title}/", headers={"Accept": "application/json"})
    return files.json()


def scanfileexists(ref):
    normtitle = ref.bibtexjson["title"].replace(" ", "_").replace("(", "").replace(")", "")
    folio = get_folio(ref)
    return f"{folio}.jpg" in iiif_files(normtitle)


def scanfile(ref):
    normtitle = ref.bibtexjson["title"].replace(" ", "_").replace("(", "").replace(")", "")
    folio = get_folio(ref)
    return f"<a href='https://iiif.acdh-dev.oeaw.ac.at/images/sicprod/{normtitle}/{folio}.jpg'>{normtitle}/{folio}</a>"


class ReferenceScanFail(LoginRequiredMixin, ListView):
    template_name = "failingreferences.html"

    def get_queryset(self, *args, **kwargs):
        refs = Reference.objects.all()
        refs = [ref for ref in refs if scanfolderexists(ref)]
        refs = [(ref, scanfile(ref)) for ref in refs if not scanfileexists(ref)]
        return refs
