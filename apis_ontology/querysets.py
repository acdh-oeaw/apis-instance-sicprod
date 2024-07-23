from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import OuterRef, Value
from django.db.models.functions import JSONObject, Concat
from apis_ontology.models import Person, Function, Place, Institution, Event, Salary


def SalaryViewSetQueryset(queryset):
    return queryset.filter(typ__in=["Sold", "Provision", "Sonstiges"])


def LegacyStuffMixinViewSetQueryset(queryset):
    space = Value(" ")

    person_subquery_a = Person.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk"))
    person_subquery_b = Person.objects.filter(triple_set_from_subj__obj_id=OuterRef("pk"))
    person_subquery = person_subquery_a | person_subquery_b
    person_subquery_json = person_subquery.values(json=JSONObject(name=Concat("first_name", space, "name"), id="id"))
    person_subquery_ids = person_subquery.values("id")

    function_subquery = Function.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk"))
    function_subquery_json = function_subquery.values(json=JSONObject(name="name", id="id"))
    function_subquery_ids = function_subquery.values("id")

    place_subquery = Place.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk"))
    place_subquery_json = place_subquery.values(json=JSONObject(name="name", id="id"))
    place_subquery_ids = place_subquery.values("id")

    institution_subquery = Institution.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk"))
    institution_subquery_json = institution_subquery.values(json=JSONObject(name="name", id="id"))
    institution_subquery_ids = institution_subquery.values("id")

    event_subquery = Event.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk"))
    event_subquery_json = event_subquery.values(json=JSONObject(name="name", id="id"))
    event_subquery_ids = event_subquery.values("id")

    salary_subquery = Salary.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk"))
    salary_subquery_json = salary_subquery.values(json=JSONObject(name="name", id="id"))
    salary_subquery_ids = salary_subquery.values("id")

    return queryset.annotate(
            related_persons=ArraySubquery(person_subquery_json),
            related_persons_ids=ArraySubquery(person_subquery_ids),
            related_functions=ArraySubquery(function_subquery_json),
            related_functions_ids=ArraySubquery(function_subquery_ids),
            related_places=ArraySubquery(place_subquery_json),
            related_places_ids=ArraySubquery(place_subquery_ids),
            related_institutions=ArraySubquery(institution_subquery_json),
            related_institutions_ids=ArraySubquery(institution_subquery_ids),
            related_events=ArraySubquery(event_subquery_json),
            related_events_ids=ArraySubquery(event_subquery_ids),
            related_salaries=ArraySubquery(salary_subquery_json),
            related_salaries_ids=ArraySubquery(salary_subquery_ids),
            )
