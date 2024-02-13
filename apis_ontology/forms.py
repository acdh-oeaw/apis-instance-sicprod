from apis_core.generic.forms import GenericModelForm
from apis_ontology.models import Person
from crispy_forms.helper import FormHelper


class PersonForm(GenericModelForm):
    field_order = ["first_name", "name", "start_date_written", "end_date_written", "status", "collection", "gender"]

    class Meta(GenericModelForm.Meta):
        model = Person
        exclude = ["published"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["collection"].initial = [1,4]
        self.helper = FormHelper()
        self.helper.form_tag = False
