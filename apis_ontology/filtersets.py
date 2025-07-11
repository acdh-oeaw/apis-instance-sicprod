import django_filters
from django.db.models import Q
from django import forms
from django.contrib.contenttypes.models import ContentType
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from apis_core.generic.forms import GenericFilterSetForm
from apis_core.collections.models import SkosCollection, SkosCollectionContentObject
from collections import OrderedDict
from apis_core.apis_entities.utils import get_entity_classes
from functools import cache
from apis_core.relations.models import Relation


ABSTRACT_ENTITY_FILTERS_EXCLUDE = ["review", "start_date", "start_start_date", "start_end_date", "end_date", "end_start_date", "end_end_date", "notes", "text", "published", "status", "references"]
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


class SicprodLegacyStuffFilterSetForm(GenericFilterSetForm):
    columns_exclude = SICPROD_FILTERS_EXCLUDE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = OrderedDict(self.fields)
        if "name" in self.fields:
            self.fields.move_to_end("name", False)
        if "columns" in self.fields:
            self.fields.move_to_end("columns", False)


class SicprodMixinFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        exclude = SICPROD_FILTERS_EXCLUDE
        form = SicprodLegacyStuffFilterSetForm


class SalaryFilterSet(SicprodMixinFilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["typ"].method = filter_empty_string
        self.filters["typ"].extra["choices"] = (*self.filters["typ"].extra["choices"], ("empty", "Nicht gesetzt"))
        self.filters["typ"].extra["required"] = False


class FunctionFilterSet(SicprodMixinFilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].method = name_alternative_name_filter
        self.filters["name"].label = "Name or alternative name"


class PlaceFilterSet(SicprodMixinFilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["type"].method = filter_empty_string
        self.filters["type"].extra["choices"] = (*self.filters["type"].extra["choices"], ("empty", "Nicht gesetzt"))
        self.filters["type"].extra["required"] = False


PERSON_FILTERS_EXCLUDE = SICPROD_FILTERS_EXCLUDE
PERSON_FILTERS_EXCLUDE.remove("status")


class PersonFilterSet(SicprodMixinFilterSet):
    class Meta(SicprodMixinFilterSet.Meta):
        exclude = PERSON_FILTERS_EXCLUDE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"].method = name_alternative_name_filter
        self.filters["name"].label = "Name or alternative name"
        self.filters["gender"].method = filter_empty_string
        self.filters["gender"].extra["choices"] = (*self.filters["gender"].extra["choices"], ("empty", "Nicht gesetzt"))
        self.filters["gender"].extra["required"] = False


class InstitutionFilterSet(SicprodMixinFilterSet):
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


class NoValidationMultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        return True

    def to_python(self, value):
        """
        We want to allow not only `?foo=a&foo=b` for lists, but also
        `?foo=a,b`, so we split each value by comma and create a new
        list from the results
        """
        values = super().to_python(value)
        values = [item for value in values for item in value.split(",")]
        return values


class FacetFilter(django_filters.CharFilter):
    field_class = NoValidationMultipleChoiceField

    def filter(self, qs, value):
        if not value:
            return qs
        if self.field_name.startswith("relation_"):
            rels = list(Relation.objects.filter(subj_object_id__in=value).values_list("obj_object_id", flat=True))
            rels += list(Relation.objects.filter(obj_object_id__in=value).values_list("subj_object_id", flat=True))
            return qs.filter(pk__in=rels).distinct()
        else:
            return qs.filter(**{f"{self.field_name}__in": value})


class FacetFilterSetMixin:
    facet_attributes = ["gender", "type", "relation_person", "relation_function", "relation_place", "relation_institution", "relation_event", "relation_salary"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for facet in self.facet_attributes:
            self.filters[f"facet_{facet}"] = FacetFilter(field_name=facet)


class SalaryApiFilterSet(FacetFilterSetMixin, SalaryFilterSet):
    pass


class FunctionApiFilterSet(FacetFilterSetMixin, FunctionFilterSet):
    pass


class PlaceApiFilterSet(FacetFilterSetMixin, PlaceFilterSet):
    pass


class PersonApiFilterSet(FacetFilterSetMixin, PersonFilterSet):
    pass


class InstitutionApiFilterSet(FacetFilterSetMixin, InstitutionFilterSet):
    pass


class EventApiFilterSet(FacetFilterSetMixin, SicprodMixinFilterSet):
    pass


@cache
def get_entity_natural_keys():
    entity_classes = get_entity_classes()
    content_types = [ContentType.objects.get_for_model(entity_class) for entity_class in entity_classes]
    content_types = [f"{content_type.app_label}.{content_type.name}" for content_type in content_types]
    return content_types


class EntityFilter(django_filters.MultipleChoiceFilter):
    def filter(self, qs, value):
        if not value:
            value = get_entity_natural_keys()
        q = Q()
        for entity in value:
            entity = entity.split(".")[1]
            q |= Q(**{f"{entity}__isnull": False})
        return qs.filter(q)


class NetworkFilterSet(django_filters.rest_framework.FilterSet):
    entities = EntityFilter(choices=list(zip(get_entity_natural_keys(), get_entity_natural_keys())))
