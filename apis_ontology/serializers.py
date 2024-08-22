import json
import re
import requests
from rest_framework import serializers
from apis_core.generic.serializers import GenericHyperlinkedModelSerializer
from apis_core.apis_relations.models import TempTriple
from django.contrib.contenttypes.models import ContentType
from apis_bibsonomy.models import Reference
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from functools import cache
import roman

DATEPATTERN = re.compile(r"(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)")
FOLIOPATTERN = re.compile(r"^(?P<cleanfolio>\d{1,3}[r|v]).*$")
ROMANPATTERN = re.compile(r"^(?P<romanfirst>[C|X|L|I|V]{1,9})(?P<rectoverso>[r|v])")


@cache
def iiif_titles():
    titles = requests.get("https://iiif.acdh-dev.oeaw.ac.at/images/sicprod/", headers={"Accept": "application/json"})
    return titles.json()


def get_folio(obj):
    folio = obj.folio
    if obj.folio:
        if match := ROMANPATTERN.match(obj.folio):
            romanfirst = match["romanfirst"]
            try:
                number = roman.fromRoman(romanfirst)
            except roman.InvalidRomanNumeralError:
                return f"Invalid roman numeral: {obj.folio}"
            if match["rectoverso"] == "r":
                number -= 1
            return  f"{roman.toRoman(number)}v-{roman.toRoman(number+1)}r"
        if match := FOLIOPATTERN.match(obj.folio):
            cleanfolio = match["cleanfolio"]
            nr = int(cleanfolio[:-1])
            if cleanfolio.endswith("r"):
                folio = f"{nr-1:03d}v-{nr:03d}r"
            if cleanfolio.endswith("v"):
                folio = f"{nr:03d}v-{nr+1:03d}r"
    return folio


class FixDateMixin:
    def fix_date(self, date):
        if date:
            if match := DATEPATTERN.search(date):
                date = date[:match.span()[0]] + match["day"] + "." + match["month"] + "." + match["year"] + date[match.span()[1]:]
        return date

    def to_representation(self, instance):
        """Convert `date` representation."""
        fields = ["start_date_written", "end_date_written"]
        ret = super().to_representation(instance)
        for field in fields:
            if ret.get(field, None):
                ret[field] = self.fix_date(ret[field])
        return ret


class SimpleObjectSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField(method_name="get_name")
    type = serializers.SerializerMethodField(method_name="get_type")

    def get_name(self, obj):
        if hasattr(obj, "first_name") and hasattr(obj, "name"):
            return f"{obj.first_name} {obj.name}"
        if hasattr(obj, "name"):
            return obj.name
        return str(obj)

    def get_type(self, obj):
        return ContentType.objects.get_for_model(obj).model


class SimplifiedReferenceSerializer(serializers.ModelSerializer):
    scan_path = serializers.SerializerMethodField()
    scandata = serializers.SerializerMethodField()

    class Meta:
        model = Reference
        fields = ["pages_start", "pages_end", "folio", "scan_path", "notes", "scandata"]

    def get_fields(self):
        fields = super().get_fields()
        fields["bibtex"] = serializers.SerializerMethodField(method_name="get_bibtex")
        return fields

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_bibtex(self, obj):
        return json.loads(obj.bibtex)

    def get_scan_path(self, obj) -> str:
        bibtex = json.loads(obj.bibtex)
        folder = bibtex["title"].replace(" ", "_")
        filename = get_folio(obj)
        return f"{folder}/{filename}.jpg"

    def get_scandata(self, obj) -> dict:
        scandata = {}
        bibtex = json.loads(obj.bibtex)
        title = bibtex["title"].replace(" ", "_").replace("(", "").replace(")", "")
        if title in iiif_titles():
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


class LegacyStuffMixinSerializer(GenericHyperlinkedModelSerializer):
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
        fields = ["id", "name", "start_date_written", "end_date_written", "type", "longitude", "latitude", "alternative_label"]

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

    def get_related_to(self, obj) -> [int]:
        return sorted(set(obj.related_to))
