import requests
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from auditlog.models import LogEntry
from apis_bibsonomy.models import Reference
from apis_ontology.serializers import iiif_titles, get_folio
from functools import cache
import django_tables2 as tables
from django.utils.html import format_html


class UserAuditLog(LoginRequiredMixin, ListView):
    def get_queryset(self, *args, **kwargs):
        return LogEntry.objects.filter(actor=self.request.user)


def scanfolderexists(ref):
    if "title" in ref.bibtexjson:
        normtitle = ref.bibtexjson["title"].replace(" ", "_").replace("(", "").replace(")", "")
        return normtitle in iiif_titles()
    return False


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


class ReferenceFailTable(tables.Table):
    ref = tables.Column(empty_values=())
    scanfile = tables.Column(empty_values=())
    on = tables.Column(empty_values=())

    def render_on(self, record):
        try:
            obj = record.referenced_object
            rep = str(obj).replace("<", "").replace(">","")
            return format_html(f"<a href='{obj.get_absolute_url()}'>{rep}</a>")
        except Exception:
            return "Referenced object does not exist."

    def render_ref(self, record):
        return str(record)

    def render_scanfile(self, record):
        return format_html(scanfile(record))


class ReferenceScanFail(LoginRequiredMixin, tables.SingleTableView):
    template_name = "failingreferences.html"
    table_class = ReferenceFailTable

    def get_queryset(self, *args, **kwargs):
        refs = Reference.objects.all()
        refs = [ref for ref in refs if scanfolderexists(ref)]
        refs = [ref for ref in refs if not scanfileexists(ref)]
        return refs
