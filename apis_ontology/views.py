from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from auditlog.models import LogEntry
from apis_bibsonomy.models import Reference
from apis_ontology.serializers import iiif_titles, get_folio, normalize_title
import django_tables2 as tables
from django.utils.html import format_html


class UserAuditLog(LoginRequiredMixin, ListView):
    def get_queryset(self, *args, **kwargs):
        return LogEntry.objects.filter(actor=self.request.user)


def scanfolderexists(ref):
    if "title" in ref.bibtexjson:
        return normalize_title(ref.bibtexjson["title"]) in iiif_titles()
    return False


def scanfolder(ref):
    normtitle = normalize_title(ref.bibtexjson["title"])
    return f"<a href='https://iiif.acdh-dev.oeaw.ac.at/images/sicprod/{normtitle}/'>{normtitle}/</a>"


class ReferenceFailTable(tables.Table):
    ref = tables.Column(empty_values=())
    folder = tables.Column(empty_values=())
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

    def render_folder(self, record):
        return format_html(scanfolder(record))


class ReferenceScanFail(LoginRequiredMixin, tables.SingleTableView):
    template_name = "failingreferences.html"
    table_class = ReferenceFailTable

    def get_queryset(self, *args, **kwargs):
        refs = Reference.objects.all()
        refs = [ref for ref in refs if scanfolderexists(ref)]
        refs = [ref for ref in refs if get_folio(ref) is None]
        return refs
