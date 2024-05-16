import django_filters
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet, ABSTRACT_ENTITY_FILTERS_EXCLUDE, AbstractEntityFilterSetForm
from apis_core.collections.models import SkosCollection, SkosCollectionContentObject
from collections import OrderedDict


SICPROD_FILTERS_EXCLUDE = ABSTRACT_ENTITY_FILTERS_EXCLUDE + ["metadata", "deprecated_name"]


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


def collection_method(queryset, name, value):
    if value:
        content_type = ContentType.objects.get_for_model(queryset.model)
        scco = SkosCollectionContentObject.objects.filter(content_type=content_type, collection__in=value).values("object_id")
        return queryset.filter(id__in=scco)
    return queryset


def collection_method_exclude(queryset, name, value):
    if value:
        content_type = ContentType.objects.get_for_model(queryset.model)
        scco = SkosCollectionContentObject.objects.filter(content_type=content_type, collection__in=value).values("object_id")
        return queryset.exclude(id__in=scco)
    return queryset


class SicprodLegacyStuffFilterSetForm(AbstractEntityFilterSetForm):
    columns_exclude = SICPROD_FILTERS_EXCLUDE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = OrderedDict(self.fields)
        self.fields.move_to_end("name", False)
        self.fields.move_to_end("columns", False)


class LegacyStuffMixinFilterSet(AbstractEntityFilterSet):
    collection = django_filters.ModelMultipleChoiceFilter(
        queryset=SkosCollection.objects.filter(parent__name="sicprod").order_by("name"),
        label="Collections",
        method=collection_method,
    )
    collection_exclude = django_filters.ModelMultipleChoiceFilter(
        queryset=SkosCollection.objects.filter(parent__name="sicprod").order_by("name"),
        label="Collections Exclude",
        method=collection_method_exclude,
    )

    class Meta(AbstractEntityFilterSet.Meta):
        exclude = SICPROD_FILTERS_EXCLUDE
        form = SicprodLegacyStuffFilterSetForm


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


# Those are simply there to remove the `metadata` which is a JSONField and makes the django-filter throw up
class SicprodVersionFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        exclude = SICPROD_FILTERS_EXCLUDE


class VersionFunctionFilterSet(SicprodVersionFilterSet):
    pass


class VersionPlaceFilterSet(SicprodVersionFilterSet):
    pass


class VersionPersonFilterSet(SicprodVersionFilterSet):
    pass


class VersionInstitutionFilterSet(SicprodVersionFilterSet):
    pass


class VersionEventFilterSet(SicprodVersionFilterSet):
    pass


class VersionSalaryFilterSet(SicprodVersionFilterSet):
    pass
