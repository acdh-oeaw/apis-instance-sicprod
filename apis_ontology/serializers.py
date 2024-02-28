from rest_framework import serializers
from apis_core.generic.serializers import GenericHyperlinkedModelSerializer, GenericHyperlinkedIdentityField
from apis_core.apis_relations.models import Triple
from django.db.models import Q


class SimpleObjectSerializer(serializers.Serializer):
    uri = GenericHyperlinkedIdentityField(view_name="foo")
    name = serializers.CharField()


class TripleSerializer(serializers.ModelSerializer):
    obj = SimpleObjectSerializer()
    subj = SimpleObjectSerializer()
    prop = SimpleObjectSerializer()

    class Meta:
        model = Triple
        exclude = ["id"]


class LegacyStuffMixinSerializer(GenericHyperlinkedModelSerializer):
    retrieve = False

    class Meta:
        fields = "__all__"

    def get_fields(self):
        fields = super().get_fields()
        if self.context["view"].action == "retrieve":
            fields["relations"] = serializers.SerializerMethodField(method_name="get_relations")
        return fields

    def get_relations(self, obj):
        relations = Triple.objects.filter(Q(obj=obj)|Q(subj=obj))
        serializer = TripleSerializer(relations, many=True, context=self.context)
        return serializer.data
