import django_tables2 as tables
from django_tables2.utils import A
from apis_core.apis_entities.tables import AbstractEntityTable


class FunctionTable(AbstractEntityTable):
    class Meta:
        fields = ["alternative_label"]
        sequence = ("desc", "...", "view", "edit", "noduplicate", "delete")


class PersonTable(AbstractEntityTable):
    class Meta:
        fields = ["name", "first_name", "start_date_written", "end_date_written", "alternative_label", "status"]
        exclude = ["desc"]
        sequence = ("...", "view", "edit", "noduplicate", "delete")
        order_by = ("name", "first_name")

    name = tables.LinkColumn()
    first_name = tables.LinkColumn()
