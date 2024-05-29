from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import OuterRef, Value
from django.db.models.functions import JSONObject, Concat
from apis_ontology.models import Person, Function, Place, Institution, Event, Salary


def SalaryViewSetQueryset(queryset):
    return queryset.filter(typ__in=["Sold", "Provision", "Sonstiges"])


def LegacyStuffMixinViewSetQueryset(queryset):
    space = Value(" ")
    person_subquery = Person.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk")).values(json=JSONObject(name=Concat("first_name", space, "name"), id="id"))
    function_subquery = Function.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk")).values(json=JSONObject(name="name", id="id"))
    place_subquery = Place.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk")).values(json=JSONObject(name="name", id="id"))
    institution_subquery = Institution.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk")).values(json=JSONObject(name="name", id="id"))
    event_subquery = Event.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk")).values(json=JSONObject(name="name", id="id"))
    salary_subquery = Salary.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk")).values(json=JSONObject(name="name", id="id"))
    return queryset.annotate(
            related_persons=ArraySubquery(person_subquery),
            related_functions=ArraySubquery(function_subquery),
            related_places=ArraySubquery(place_subquery),
            related_institutions=ArraySubquery(institution_subquery),
            related_events=ArraySubquery(event_subquery),
            related_salaries=ArraySubquery(salary_subquery),
            )
