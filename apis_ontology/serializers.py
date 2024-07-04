import json
from rest_framework import serializers
from apis_core.generic.serializers import GenericHyperlinkedModelSerializer
from apis_core.apis_relations.models import TempTriple
from django.contrib.contenttypes.models import ContentType
from apis_bibsonomy.models import Reference
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


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
    class Meta:
        model = Reference
        fields = ["pages_start", "pages_end", "folio"]

    def get_fields(self):
        fields = super().get_fields()
        fields["bibtex"] = serializers.SerializerMethodField(method_name="get_bibtex")
        return fields

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_bibtex(self, obj):
        return json.loads(obj.bibtex)


class TempTripleSerializer(serializers.ModelSerializer):
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


class SicprodSerializer(GenericHyperlinkedModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        fields["relation_types"] = serializers.SerializerMethodField(method_name="get_relation_types")
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


class ReferencesMixin(serializers.Serializer):
    references = serializers.SerializerMethodField(method_name="get_references")

    @extend_schema_field(SimplifiedReferenceSerializer(many=True))
    def get_references(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        references = Reference.objects.filter(content_type=ct, object_id=obj.id)
        return SimplifiedReferenceSerializer(references, many=True).data


class EventListSerializer(SicprodSerializer, serializers.ListSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "type"]


class EventSerializer(ReferencesMixin, SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "type", "references"]
        list_serializer_class = EventListSerializer


class FunctionListSerializer(SicprodSerializer, serializers.ListSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "alternative_label"]


class FunctionSerializer(ReferencesMixin, SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "alternative_label", "references"]
        list_serializer_class = FunctionListSerializer


class InstitutionListSerializer(SicprodSerializer, serializers.ListSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "type", "alternative_label"]


class InstitutionSerializer(ReferencesMixin, SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "type", "alternative_label", "references"]
        list_serializer_class = InstitutionListSerializer


class PersonListSerializer(SicprodSerializer, serializers.ListSerializer):
    class Meta:
        fields = ["id", "url", "name", "start_date_written", "end_date_written", "status", "first_name", "gender", "alternative_label"]


class PersonSerializer(ReferencesMixin, SicprodSerializer):
    class Meta:
        fields = ["id", "url", "name", "start_date_written", "end_date_written", "status", "first_name", "gender", "alternative_label", "references"]
        list_serializer_class = PersonListSerializer


class PlaceListSerializer(SicprodSerializer, serializers.ListSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "type", "longitude", "latitude", "alternative_label"]


class PlaceSerializer(ReferencesMixin, SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "type", "longitude", "latitude", "alternative_label", "references"]
        list_serializer_class = PlaceListSerializer


class SalaryListSerializer(SicprodSerializer, serializers.ListSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "typ", "repetitionType"]


class SalarySerializer(ReferencesMixin, SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "typ", "repetitionType", "references"]
        list_serializer_class = SalaryListSerializer
