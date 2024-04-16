import json
from rest_framework import serializers
from apis_core.generic.serializers import GenericHyperlinkedModelSerializer
from apis_core.apis_relations.models import TempTriple
from django.contrib.contenttypes.models import ContentType
from apis_bibsonomy.models import Reference


class SimpleObjectSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField(method_name="get_name")

    def get_name(self, obj):
        if hasattr(obj, "first_name") and hasattr(obj, "name"):
            return f"{obj.first_name} {obj.name}"
        if hasattr(obj, "name"):
            return obj.name
        return str(obj)


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

    def __init__(self, *args, **kwargs):
        self.reverse = kwargs.pop("reverse", False)
        super().__init__(*args, **kwargs)

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

    def get_to(self, obj):
        if self.reverse:
            return SimpleObjectSerializer(obj.subj).data
        return SimpleObjectSerializer(obj.obj).data

    def get_name(self, obj):
        if self.reverse:
            return obj.prop.name_reverse
        return obj.prop.name_forward

    def get_references(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        references = Reference.objects.filter(content_type=ct, object_id=obj.id)
        return ReferenceSerializer(references, many=True).data


class LegacyStuffMixinSerializer(GenericHyperlinkedModelSerializer):
    class Meta:
        fields = ["name"]


class PersonSerializer(GenericHyperlinkedModelSerializer):
    retrieve = False

    class Meta:
        fields = ["url", "name", "start_date_written", "end_date_written", "status", "first_name", "gender", "alternative_label"]

    def get_fields(self):
        fields = super().get_fields()
        if self.context["view"].action == "retrieve":
            fields["relations"] = serializers.SerializerMethodField(method_name="get_relations")
            fields["references"] = serializers.SerializerMethodField(method_name="get_references")
        return fields

    def get_relations(self, obj):
        forward_relations = TempTriple.objects.filter(subj=obj).prefetch_related("subj", "obj", "prop")
        reverse_relations = TempTriple.objects.filter(obj=obj).prefetch_related("subj", "obj", "prop")
        relations = {}
        for relation in forward_relations:
            reltype = ContentType.objects.get_for_model(relation.obj).model
            if reltype not in relations:
                relations[reltype] = []
            relations[reltype].append(TempTripleSerializer(relation).data)
        for relation in reverse_relations:
            reltype = ContentType.objects.get_for_model(relation.subj).model
            if reltype not in relations:
                relations[reltype] = []
            relations[reltype].append(TempTripleSerializer(relation, reverse=True).data)
        return relations

    def get_references(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        references = Reference.objects.filter(content_type=ct, object_id=obj.id)
        return ReferenceSerializer(references, many=True).data
