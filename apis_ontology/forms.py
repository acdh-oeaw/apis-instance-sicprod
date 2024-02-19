from apis_core.generic.forms import GenericModelForm
from apis_ontology.models import Person


class LegacyStuffMixinForm(GenericModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["collection"].initial = [1, 4]


class PersonForm(LegacyStuffMixinForm):
    field_order = ["first_name", "name", "start_date_written", "end_date_written", "status", "collection", "gender"]

    class Meta(GenericModelForm.Meta):
        model = Person
        exclude = ["published"]


class PlaceForm(LegacyStuffMixinForm):
    field_order = ["name", "type", "latitude", "longitude", "status", "collection"]


class InstitutionForm(LegacyStuffMixinForm):
    field_order = ["name", "start_date_written", "end_date_written", "kind", "status", "collection"]
