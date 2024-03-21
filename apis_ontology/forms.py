from apis_core.generic.forms import GenericModelForm
from apis_ontology.models import Person

from apis_core.generic.forms.widgets import NewlineSeparatedListWidget


class LegacyStuffMixinForm(GenericModelForm):
    class Meta(GenericModelForm.Meta):
        exclude = ["deprecated_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["collection"].initial = [1, 4]
        self.fields["alternative_label"].widget = NewlineSeparatedListWidget(attrs={"class": "mb-1"})


class PersonForm(LegacyStuffMixinForm):
    field_order = ["first_name", "name", "start_date_written", "end_date_written", "status", "collection", "gender"]

    class Meta(LegacyStuffMixinForm.Meta):
        model = Person
        exclude = ["published", "deprecated_name"]


class PlaceForm(LegacyStuffMixinForm):
    field_order = ["name", "type", "latitude", "longitude", "status", "collection"]


class InstitutionForm(LegacyStuffMixinForm):
    field_order = ["name", "start_date_written", "end_date_written", "kind", "status", "collection"]
