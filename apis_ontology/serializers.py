from rest_framework import serializers
from apis_core.generic.serializers import GenericHyperlinkedModelSerializer, GenericHyperlinkedIdentityField
from apis_core.apis_relations.models import TempTriple
from django.contrib.contenttypes.models import ContentType


class SimpleObjectSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class TempTripleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempTriple
        fields = ['start_date_written', 'end_date_written', 'start_start_date', 'start_end_date', 'end_start_date', 'end_end_date', 'notes']

    def __init__(self, *args, **kwargs):
        self.reverse = kwargs.pop("reverse", False)
        super().__init__(*args, **kwargs)

    def get_fields(self):
        fields = super().get_fields()
        fields["to"] = serializers.SerializerMethodField(method_name="get_to")
        fields["name"] = serializers.SerializerMethodField(method_name="get_name")
        return fields

    def get_to(self, obj):
        if self.reverse:
            return SimpleObjectSerializer(obj.subj).data
        return SimpleObjectSerializer(obj.obj).data

    def get_name(self, obj):
        if self.reverse:
            return obj.prop.name_reverse
        return obj.prop.name_forward


class LegacyStuffMixinSerializer(GenericHyperlinkedModelSerializer):
    retrieve = False

    class Meta:
        fields = ["url", "name", "start_date_written", "end_date_written", "status", "first_name", "gender", "alternative_label"]

    def get_fields(self):
        fields = super().get_fields()
        if self.context["view"].action == "retrieve":
            fields["relations"] = serializers.SerializerMethodField(method_name="get_relations")
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
