from django.db.models import Q

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
