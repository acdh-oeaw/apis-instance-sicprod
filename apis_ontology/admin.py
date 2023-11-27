from django.contrib import admin
from .models import Person, Function, Place, Institution, Event, Salary


@admin.register(Person, Function, Place, Institution, Event, Salary)
class EntityAdmin(admin.ModelAdmin):
    pass
