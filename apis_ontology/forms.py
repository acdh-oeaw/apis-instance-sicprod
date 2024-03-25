from apis_core.generic.forms import GenericModelForm
from apis_ontology.models import Person
from apis_core.collections.models import SkosCollection, SkosCollectionContentObject
from django import forms
from django.contrib.contenttypes.models import ContentType


class MyModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    pass


class LegacyStuffMixinForm(GenericModelForm):
    collections = MyModelMultipleChoiceField(queryset=SkosCollection.objects.filter(parent=SkosCollection.objects.get(name="sicprod")), required=False)

    class Meta(GenericModelForm.Meta):
        exclude = ["deprecated_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = SkosCollection.objects.get(name="sicprod")
        if instance := kwargs.get("instance"):
            ct = ContentType.objects.get_for_model(instance)
            sccos = SkosCollectionContentObject.objects.filter(collection__parent=self.parent, content_type=ct, object_id=instance.pk).values_list("collection")
            self.fields["collections"].initial = SkosCollection.objects.filter(id__in=sccos)
        else:
            self.fields["collections"].initial = [2, 5]

        #self.fields["collection"].initial = [1, 4]

    def save(self, *args, **kwargs):
        obj = super().save(*args, **kwargs)
        ct = ContentType.objects.get_for_model(obj)
        collections = SkosCollection.objects.filter(parent=self.parent)
        for skoscollection in self.cleaned_data["collections"]:
            scco, _ = SkosCollectionContentObject.objects.get_or_create(collection=skoscollection, content_type=ct, object_id=obj.pk)
        SkosCollectionContentObject.objects.filter(collection__in=collections, content_type=ct, object_id=obj.pk,).exclude(collection__in=self.cleaned_data["collections"]).delete()
        return obj


class PersonForm(LegacyStuffMixinForm):
    field_order = ["first_name", "name", "start_date_written", "end_date_written", "status", "collection", "gender", "alternative_label"]

    class Meta(LegacyStuffMixinForm.Meta):
        model = Person
        exclude = ["published", "deprecated_name"]


class PlaceForm(LegacyStuffMixinForm):
    field_order = ["name", "type", "latitude", "longitude", "status", "collection"]


class InstitutionForm(LegacyStuffMixinForm):
    field_order = ["name", "start_date_written", "end_date_written", "kind", "status", "collection"]
