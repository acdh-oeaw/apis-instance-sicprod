from apis_core.generic.forms import GenericModelForm
from apis_ontology.models import Person


from apis_core.generic.forms.widgets import NewlineSeparatedListWidget


class SicprodMixinForm(GenericModelForm):

    class Meta(GenericModelForm.Meta):
        exclude = ["deprecated_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.fields["collections"].initial:
            self.fields["collections"].initial = [2, 5]

        if "alternative_label" in self.fields:
            self.fields["alternative_label"].widget = NewlineSeparatedListWidget(attrs={"class": "mb-1"})


class PersonForm(SicprodMixinForm):
    field_order = ["first_name", "name", "start_date_written", "end_date_written", "status", "collection", "gender", "alternative_label"]

    class Meta(SicprodMixinForm.Meta):
        model = Person
        exclude = ["published", "deprecated_name"]


class PlaceForm(SicprodMixinForm):
    field_order = ["label", "type", "latitude", "longitude", "status", "collection"]


class InstitutionForm(SicprodMixinForm):
    field_order = ["name", "start_date_written", "end_date_written", "kind", "status", "collection"]


class EventForm(SicprodMixinForm):
    field_order = ["name", "start_date_written", "end_date_written", "kind", "status", "collection"]


class FunctionForm(SicprodMixinForm):
    field_order = ["name", "start_date_written", "end_date_written", "kind", "status", "collection"]


class SalaryForm(SicprodMixinForm):
    field_order = ["name", "start_date_written", "end_date_written", "kind", "status", "collection"]
