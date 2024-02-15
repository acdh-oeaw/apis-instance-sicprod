from django.db.models import Q
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet, ABSTRACT_ENTITY_FILTERS_EXCLUDE


SICPROD_FILTERS_EXCLUDE = ABSTRACT_ENTITY_FILTERS_EXCLUDE + ["metadata"]


def name_first_name_alternative_name_filter(queryset, name, value):
    return queryset.filter(
        Q(name__icontains=value) |
        Q(first_name__icontains=value) |
        Q(alternative_label__icontains=value))


def name_alternative_name_filter(queryset, name, value):
    return queryset.filter(
        Q(name__icontains=value) |
        Q(alternative_label__icontains=value))


def filter_empty_string(queryset, name, value):
    if value == "empty":
        value = ""
    lookup = f"{name}__exact"
    return queryset.filter(**{lookup: value})


def filter_status(queryset, name, value):
    return queryset.filter(status__icontains=value)


class LegacyStuffMixinFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        exclude = SICPROD_FILTERS_EXCLUDE


class SalaryFilterSet(LegacyStuffMixinFilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["typ"].method = filter_empty_string
        self.filters["typ"].extra["choices"] = (*self.filters["typ"].extra["choices"], ("empty", "Nicht gesetzt"))
        self.filters["typ"].extra["required"] = False


class FunctionFilterSet(LegacyStuffMixinFilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].method = name_alternative_name_filter
        self.filters["name"].label = "Name or alternative name"


class PlaceFilterSet(LegacyStuffMixinFilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["type"].method = filter_empty_string
        self.filters["type"].extra["choices"] = (*self.filters["type"].extra["choices"], ("empty", "Nicht gesetzt"))
        self.filters["type"].extra["required"] = False


PERSON_FILTERS_EXCLUDE = SICPROD_FILTERS_EXCLUDE
PERSON_FILTERS_EXCLUDE.remove("status")


class PersonFilterSet(LegacyStuffMixinFilterSet):
    class Meta(LegacyStuffMixinFilterSet.Meta):
        exclude = PERSON_FILTERS_EXCLUDE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].method = name_alternative_name_filter
        self.filters["name"].label = "Name or alternative name"
        self.filters["gender"].method = filter_empty_string
        self.filters["gender"].extra["choices"] = (*self.filters["gender"].extra["choices"], ("empty", "Nicht gesetzt"))
        self.filters["gender"].extra["required"] = False


class InstitutionFilterSet(LegacyStuffMixinFilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].method = name_alternative_name_filter
