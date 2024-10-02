import json
import logging
import re
import pathlib
from rest_framework import serializers
from apis_core.generic.serializers import GenericHyperlinkedModelSerializer
from apis_core.apis_relations.models import TempTriple
from django.contrib.contenttypes.models import ContentType
from apis_bibsonomy.models import Reference
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from apis_ontology.models import Salary

logger = logging.getLogger(__name__)

DATEPATTERN = re.compile(r"(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)")
FOLIOPATTERN = re.compile(r"^(?P<cleanfolio>\d{1,3}[r|v]).*$")
ROMANPATTERN = re.compile(r"^(?P<romanfirst>[C|X|L|I|V]{1,9})(?P<rectoverso>[r|v])")
PAGEPATTERN = re.compile(r"^(?P<page>\d{1,3}).*$")


def iiif_titles():
    data = json.loads(pathlib.Path("data/iiif.json").read_text())
    return data


def normalize_title(title: str) -> str:
    return title.replace(" ", "_").replace("(", "").replace(")", "")


NUMBER = re.compile(r"(?P<number>\d+)")


def get_folio(obj):
    title = normalize_title(obj.bibtexjson["title"])
    if page := obj.pages_start:
        page = f"{page:03d}"
    if obj.folio:
        page = obj.folio
        if "-" in obj.folio:
            page = obj.folio.split("-")[0]
        if "–" in obj.folio:
            page = obj.folio.split("–")[0]
        if page.endswith("v") or page.endswith("r"):
            suffix = page[-1:]
        if page:
            if match := NUMBER.match(page):
                page = match["number"]
        if page.endswith("v") or page.endswith("r"):
            page = page[:-1]
        try:
            page = int(page)
            page = f"{page:03d}{suffix}"
        except Exception:
            pass
    if page:
        matches = [scanfile for scanfile in iiif_titles()[title] if str(page) in scanfile]
        if matches:
            return matches[0]
    print(obj.folio)
    print(page)
    return None


class FixDateMixin:
    def fix_date(self, date):
        """
        replace YYYY-MM-DD with YYYY.MM.DD format
        """
        if date:
            if match := DATEPATTERN.search(date):
                date = date[:match.span()[0]] + match["day"] + "." + match["month"] + "." + match["year"] + date[match.span()[1]:]
        return date

    def to_representation(self, instance):
        """Convert `date` representation."""
        written_date_fields = ["start_date_written", "end_date_written"]
        ret = super().to_representation(instance)
        for field in written_date_fields:
            if ret.get(field, None):
                ret[field] = self.fix_date(ret[field])
        # if we are working with a relation that relates
        # to a salary, make the date fields only return the year
        if isinstance(instance, TempTriple):
            if isinstance(instance.subj, Salary) or isinstance(instance.obj, Salary):
                if start_date := getattr(instance, "start_date"):
                    ret["start_date"] = str(start_date.year)
                    ret["start_date_written"] = str(start_date.year)
                if end_date := getattr(instance, "end_date"):
                    ret["end_date"] = str(end_date.year)
                    ret["end_date_written"] = str(end_date.year)
        return ret


class SimpleObjectSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField(method_name="get_name")
    type = serializers.SerializerMethodField(method_name="get_type")

    def get_name(self, obj):
        if getattr(obj, "first_name", None) and getattr(obj, "name", None):
            return f"{obj.first_name} {obj.name}"
        if hasattr(obj, "name"):
            return obj.name
        return str(obj)

    def get_type(self, obj):
        return ContentType.objects.get_for_model(obj).model


class SimplifiedReferenceSerializer(serializers.ModelSerializer):
    scandata = serializers.SerializerMethodField()

    class Meta:
        model = Reference
        fields = ["pages_start", "pages_end", "folio", "notes", "scandata"]

    def get_fields(self):
        fields = super().get_fields()
        fields["bibtex"] = serializers.SerializerMethodField(method_name="get_bibtex")
        return fields

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_bibtex(self, obj):
        return json.loads(obj.bibtex)

    def get_scandata(self, obj) -> dict:
        scandata = {}
        bibtex = json.loads(obj.bibtex)
        title = normalize_title(bibtex["title"])
        if title in iiif_titles().keys():
            scandata["title"] = title
            folio = get_folio(obj)
            scandata["pages"] = folio or f"{obj.pages_start}-{obj.pages_end}"
        return scandata


class TempTripleSerializer(FixDateMixin, serializers.ModelSerializer):
    class Meta:
        model = TempTriple
        fields = ['start_date_written', 'end_date_written', 'start_date', 'end_date', 'notes']

    def get_fields(self):
        fields = super().get_fields()
        fields["to"] = serializers.SerializerMethodField(method_name="get_to")
        fields["name"] = serializers.SerializerMethodField(method_name="get_name")
        fields["references"] = serializers.SerializerMethodField(method_name="get_references")
        fields["family_relation"] = serializers.SerializerMethodField(method_name="get_family_relation")
        return fields

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_family_relation(self, obj):
        if self.get_name(obj) in ["hat Ehe mit", "ist Bruder/Schwester von", "hat Familienbeziehung zu", "ist Kind von", "ist Elternteil von"]:
            return True
        return False

    @extend_schema_field(SimpleObjectSerializer())
    def get_to(self, obj):
        if self.context["obj"] == obj.obj:
            return SimpleObjectSerializer(obj.subj).data
        return SimpleObjectSerializer(obj.obj).data

    def get_name(self, obj):
        if self.context["obj"] == obj.obj:
            return obj.prop.name_reverse
        return obj.prop.name_forward

    @extend_schema_field(SimplifiedReferenceSerializer(many=True))
    def get_references(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        references = Reference.objects.filter(content_type=ct, object_id=obj.id)
        return SimplifiedReferenceSerializer(references, many=True).data


class SicprodMixinSerializer(GenericHyperlinkedModelSerializer):
    class Meta:
        fields = ["name"]


class SicprodSerializer(FixDateMixin, GenericHyperlinkedModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        fields["relation_types"] = serializers.SerializerMethodField(method_name="get_relation_types")
        fields["references"] = serializers.SerializerMethodField(method_name="get_references")
        return fields

    def get_relation_types(self, obj) -> list[str]:
        forward_relations = TempTriple.objects.filter(subj=obj).prefetch_related("subj", "obj")
        reverse_relations = TempTriple.objects.filter(obj=obj).prefetch_related("subj", "obj")
        relations = set()
        for relation in forward_relations:
            reltype = ContentType.objects.get_for_model(relation.obj).model
            relations.add(reltype)
        for relation in reverse_relations:
            reltype = ContentType.objects.get_for_model(relation.subj).model
            relations.add(reltype)
        return relations

    @extend_schema_field(SimplifiedReferenceSerializer(many=True))
    def get_references(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        references = Reference.objects.filter(content_type=ct, object_id=obj.id)
        return SimplifiedReferenceSerializer(references, many=True).data


class EventSerializer(SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "type"]


class FunctionSerializer(SicprodSerializer):
    alternative_label = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "alternative_label"]

    def get_alternative_label(self, obj) -> list[str]:
        return obj.alternative_label.splitlines()


class InstitutionSerializer(SicprodSerializer):
    alternative_label = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "type", "alternative_label"]

    def get_alternative_label(self, obj) -> list[str]:
        return obj.alternative_label.splitlines()


class PersonSerializer(SicprodSerializer):
    alternative_label = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "url", "name", "start_date_written", "end_date_written", "status", "first_name", "gender", "alternative_label"]

    def get_alternative_label(self, obj) -> list[str]:
        return obj.alternative_label.splitlines()


class PlaceSerializer(SicprodSerializer):
    alternative_label = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "label", "start_date_written", "end_date_written", "type", "longitude", "latitude", "alternative_label"]

    def get_alternative_label(self, obj) -> list[str]:
        return obj.alternative_label.splitlines()


class SalarySerializer(SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "typ", "repetitionType"]


class NetworkSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    related_to = serializers.SerializerMethodField()

    def get_name(self, obj) -> str:
        return str(obj)

    def get_type(self, obj) -> str:
        content_type = ContentType.objects.get_for_model(obj)
        return content_type.name

    def get_related_to(self, obj) -> list[int]:
        return sorted(set(obj.related_to))
