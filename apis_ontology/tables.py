import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from apis_core.relations.tables import RelationsListTable
from apis_core.generic.tables import CustomTemplateColumn


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


class ReferenceColumn(CustomTemplateColumn):
    template_name = "columns/reference.html"


class SicprodMixinRelationsTable(RelationsListTable):
    start = tables.Column(order_by="start_date_sort")
    end = tables.Column(order_by="end_date_sort")
    reference = ReferenceColumn()

    class Meta(RelationsListTable.Meta):
        per_page = 1000
