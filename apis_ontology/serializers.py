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


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ["pages_start", "pages_end", "folio"]

    def get_fields(self):
        fields = super().get_fields()
        fields["bibtex"] = serializers.SerializerMethodField(method_name="get_bibtex")
        return fields

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

    def get_family_relation(self, obj):
        if self.get_name(obj) in ["hat Ehe mit", "ist Bruder/Schwester von", "hat Familienbeziehung zu", "ist Kind von", "ist Elternteil von"]:
            return True
        return False

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_to(self, obj):
        if self.context["obj"] == obj.obj:
            return SimpleObjectSerializer(obj.subj).data
        return SimpleObjectSerializer(obj.obj).data

    def get_name(self, obj):
        if self.context["obj"] == obj.obj:
            return obj.prop.name_reverse
        return obj.prop.name_forward

    def get_references(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        references = Reference.objects.filter(content_type=ct, object_id=obj.id)
        return ReferenceSerializer(references, many=True).data


class LegacyStuffMixinSerializer(GenericHyperlinkedModelSerializer):
    class Meta:
        fields = ["name"]


class SicprodSerializer(GenericHyperlinkedModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        if self.context["view"].action == "retrieve":
            fields["relation_types"] = serializers.SerializerMethodField(method_name="get_relation_types")
            fields["references"] = serializers.SerializerMethodField(method_name="get_references")
        return fields

    def get_relation_types(self, obj):
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

    def get_references(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        references = Reference.objects.filter(content_type=ct, object_id=obj.id)
        return ReferenceSerializer(references, many=True).data


class EventSerializer(SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "type"]


class FunctionSerializer(SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "alternative_label"]


class InstitutionSerializer(SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "type", "alternative_label"]


class PersonSerializer(SicprodSerializer):
    class Meta:
        fields = ["id", "url", "name", "start_date_written", "end_date_written", "status", "first_name", "gender", "alternative_label"]


class PlaceSerializer(SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "type", "longitude", "latitude", "alternative_label"]


class SalarySerializer(SicprodSerializer):
    class Meta:
        fields = ["id", "name", "start_date_written", "end_date_written", "typ", "repetitionType"]
