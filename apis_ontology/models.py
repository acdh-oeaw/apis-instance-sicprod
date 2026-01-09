from django.db import models
from django.contrib.contenttypes.models import ContentType
from apis_core.apis_entities.models import AbstractEntity
from .legacydatemixin import LegacyDateMixin
from apis_core.collections.models import SkosCollection, SkosCollectionContentObject
from apis_core.history.models import VersionMixin
from apis_core.apis_entities.abc import E53_Place
from apis_core.relations.models import Relation
from django_interval.fields import FuzzyDateParserField

from auditlog.registry import auditlog


class SicprodMixin(models.Model):
    """ A mixin providing generic fields and functionality for all Sicprod Models """
    review = review = models.BooleanField(default=False, help_text="Should be set to True, if the data record holds up quality standards.")
    status = models.CharField(max_length=100, blank=True)
    references = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)
    metadata = models.JSONField(null=True, blank=True, editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        if self.name != "":
            return "{} (ID: {})".format(self.name, self.id)
        return "(ID: {})".format(self.id)

    def sicprod_collections(self):
        my_sccos = SkosCollection.objects.by_instance(instance=self)
        sicprod_c = SkosCollection.objects.get(name="sicprod")
        collection_c_t = ContentType.objects.get_for_model(SkosCollection)
        sccos = SkosCollectionContentObject.objects.filter(collection=sicprod_c, content_type=collection_c_t)
        return my_sccos.filter(id__in=[scco.content_object.id for scco in sccos])


class Person(VersionMixin, SicprodMixin, LegacyDateMixin, AbstractEntity):
    """
    Person, eine Subklasse von crm:E21_Person.
    """
    _default_search_fields = ["first_name", "name", "alternative_label"]
    first_name = models.CharField(max_length=1024, blank=True, null=True, verbose_name = "Vorname", help_text = "Vorname der Person.")
    name = models.CharField(max_length=255, verbose_name="Name", blank=True)
    GENDER_CHOICES = (("männlich", "männlich"), ("weiblich", "weiblich"), ("unbekannt", "unbekannt"), )
    gender = models.CharField(max_length=9, choices=GENDER_CHOICES, blank=True, verbose_name = "Geschlecht", help_text = "Geschlecht der Person.")
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternative Namen", help_text = "Feld um alternative Namen anzugeben.")

    class Meta:
        ordering = ["name", "first_name"]

    def __str__(self):
        return "{}, {} (ID: {})".format(self.name, self.first_name, self.id)


class Function(VersionMixin, SicprodMixin, LegacyDateMixin, AbstractEntity):
    """
    Eine Funktion kann von einer Person an einer Institution oder einem Hof ausgeübt werden kann.
    """
    _default_search_fields = ["name", "alternative_label"]
    name = models.CharField(max_length=255, verbose_name="Name", blank=True)
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Andere Namen für die Funktion.")

    class Meta:
        ordering = ["name"]


class Place(VersionMixin, SicprodMixin, LegacyDateMixin, E53_Place, AbstractEntity):
    """
    Orte in SiCProD, Subklasse von crm:E53_Place.
    """
    _default_search_fields = ["label", "alternative_label"]
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Alternativer Name für einen Ort.")
    TYPE_CHOICES = (("Stadt", "Stadt"), ("Dorf/Nachbarschaft/Gemein/Siedlung/Weiler", "Dorf/Nachbarschaft/Gemein/Siedlung/Weiler"), ("Burg/Schloss", "Burg/Schloss"), ("Land/Herrschaftskomplex", "Land/Herrschaftskomplex"), ("Landschaft/Region", "Landschaft/Region"), ("Lehen", "Lehen"), ("Haus/Hof", "Haus/Hof"), ("Gericht", "Gericht"), ("Kloster", "Kloster"), ("Gewässer", "Gewässer"), ("Grundherrschaft", "Grundherrschaft"), ("Hofmark", "Hofmark"), ("Tal", "Tal"), ("Berg", "Berg"), ("Bergrevier", "Bergrevier"), ("Pflege", "Pflege"), ("(Land-)Vogtei", "(Land-)Vogtei"), ("Propstei", "Propstei"), )
    type = models.CharField(max_length=41, choices=TYPE_CHOICES, blank=True, verbose_name = "Typ", help_text = "Art des Ortes.")

    class Meta:
        ordering = ["label"]


    def __str__(self):
        return self.label


class Institution(VersionMixin, SicprodMixin, LegacyDateMixin, AbstractEntity):
    """
    SiCProD Institution, Subklasse von crm:E74_Group. Wird für alle Institutionen benutzt die kein Hof sind
    """
    _default_search_fields = ["name", "alternative_label"]
    name = models.CharField(max_length=255, verbose_name="Name", blank=True)
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Alternativer Name der Institution.")
    TYPE_CHOICES = (("Kanzlei", "Kanzlei"), ("Hofkapelle", "Hofkapelle"), ("Küche", "Küche"), ("(Dom-)Kapitel", "(Dom-)Kapitel"), ("Universität", "Universität"), ("Kloster", "Kloster"), ("Frauenzimmer", "Frauenzimmer"), ("Bistum", "Bistum"), ("Pfarrei", "Pfarrei"), )
    type = models.CharField(max_length=13, choices=TYPE_CHOICES, blank=True, verbose_name = "Typ", help_text = "Art der institution.")

    class Meta:
        ordering = ["name"]


class Event(VersionMixin, SicprodMixin, LegacyDateMixin, AbstractEntity):
    """
    SiCProD Ereignis, Subklasse von crm:E5_Event.
    """
    _default_search_fields = ["name", "alternative_label"]
    name = models.CharField(max_length=255, verbose_name="Name", blank=True)
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Alternativer Name.")
    TYPE_CHOICES = (("Hochzeit", "Hochzeit"), ("Landtag", "Landtag"), ("Fest/Turnier", "Fest/Turnier"), ("Schlacht", "Schlacht"), ("Gesandtschaft/Reise", "Gesandtschaft/Reise"), ("Taufe", "Taufe"), ("Amtseinsetzung", "Amtseinsetzung"), ("Reichstag", "Reichstag"), )
    type = models.CharField(max_length=19, choices=TYPE_CHOICES, blank=True, verbose_name = "Typ", help_text = "Typ des Ereignisses.")

    class Meta:
        ordering = ["name"]


class Salary(VersionMixin, SicprodMixin, LegacyDateMixin, AbstractEntity):
    """
    Ein Gehalt ist die Menge an Geld die eine Person als Gegenleistung erhalten hat. Das Gehalt muss keine wiederkehrende Zahlung sein.
    """
    _default_search_fields = ["name"]
    name = models.CharField(max_length=255, verbose_name="Name", blank=True)
    TYP_CHOICES = (("Sold", "Sold"), ("Zehrung", "Zehrung"), ("Provision", "Provision"), ("Kredit", "Kredit"), ("Sonstiges", "Sonstiges"), ("Burghut", "Burghut"), ("Botenlohn", "Botenlohn"), )
    typ = models.CharField(max_length=9, choices=TYP_CHOICES, blank=True, verbose_name = "Typ", help_text = "Art des Gehalts.")
    REPETITIONTYPE_CHOICES = (("einfach", "einfach"), ("wiederholend", "wiederholend"), )
    repetitionType = models.CharField(max_length=12, choices=REPETITIONTYPE_CHOICES, blank=True, verbose_name = "Typ Wiederholungen", help_text = "Typ des Gehalts.")

    class Meta:
        ordering = ["name"]


auditlog.register(Person, serialize_data=True)
auditlog.register(Function, serialize_data=True)
auditlog.register(Place, serialize_data=True)
auditlog.register(Institution, serialize_data=True)
auditlog.register(Event, serialize_data=True)
auditlog.register(Salary, serialize_data=True)


class Bewohnt(VersionMixin, Relation):
    _legacy_property_id = 1
    subj_model = Person
    obj_model = Place

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "bewohnt"

    @classmethod
    def reverse_name(self) -> str:
        return "hat als Bewohner"


class Besitzt(VersionMixin, Relation):
    _legacy_property_id = 2
    subj_model = Person
    obj_model = Place

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "besitzt"

    @classmethod
    def reverse_name(self) -> str:
        return "ist im Besitz von"


class HatKorrespondenzMit(VersionMixin, Relation):
    _legacy_property_id = 3
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "hat Korrespondenz mit"

    @classmethod
    def reverse_name(self) -> str:
        return "hat Korrespondenz mit"


class HatFamilienbeziehungZu(VersionMixin, Relation):
    _legacy_property_id = 4
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "hat Familienbeziehung zu"

    @classmethod
    def reverse_name(self) -> str:
        return "hat Familienbeziehung zu"


class HatEheMit(VersionMixin, Relation):
    _legacy_property_id = 5
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "hat Ehe mit"

    @classmethod
    def reverse_name(self) -> str:
        return "hat Ehe mit"


class Empfiehlt(VersionMixin, Relation):
    _legacy_property_id = 7
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "empfiehlt"

    @classmethod
    def reverse_name(self) -> str:
        return "wird empfohlen von"


class HatGeschaeftsbeziehungZu(VersionMixin, Relation):
    _legacy_property_id = 8
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "hat Geschäftsbeziehung zu"

    @classmethod
    def reverse_name(self) -> str:
        return "hat Geschäftsbeziehung zu"


class IstMitgliedVon(VersionMixin, Relation):
    _legacy_property_id = 9
    subj_model = Person
    obj_model = Institution

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist Mitglied von"

    @classmethod
    def reverse_name(self) -> str:
        return "hat Mitglied"


class NimmtTeilAn(VersionMixin, Relation):
    _legacy_property_id = 10
    subj_model = Person
    obj_model = Event

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "nimmt teil an"

    @classmethod
    def reverse_name(self) -> str:
        return "hat als Teilnehmer"


class WirdAusbezahltAnPerson(VersionMixin, Relation):
    _legacy_property_id = 11
    subj_model = Salary
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "wird ausbezahlt an"

    @classmethod
    def reverse_name(self) -> str:
        return "erhält"


class IstAn(VersionMixin, Relation):
    _legacy_property_id = 12
    subj_model = Function
    obj_model = Institution

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist an"

    @classmethod
    def reverse_name(self) -> str:
        return "hat Funktion"


class WirdAusgeuebtVon(VersionMixin, Relation):
    _legacy_property_id = 13
    subj_model = Function
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "wird ausgeübt von"

    @classmethod
    def reverse_name(self) -> str:
        return "hat Funktion inne"


class IstTeilVon(VersionMixin, Relation):
    _legacy_property_id = 14
    subj_model = Place
    obj_model = Place

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist Teil von"

    @classmethod
    def reverse_name(self) -> str:
        return "hat als Teil"


class InstitutionFuehrtDurch(VersionMixin, Relation):
    _legacy_property_id = 15
    subj_model = Institution
    obj_model = Salary

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "führt durch"

    @classmethod
    def reverse_name(self) -> str:
        return "wird durchgeführt von"


class IstBruderSchwesterVon(VersionMixin, Relation):
    _legacy_property_id = 143
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist Bruder/Schwester von"

    @classmethod
    def reverse_name(self) -> str:
        return "ist Bruder/Schwester von"


class IstKindVon(VersionMixin, Relation):
    _legacy_property_id = 144
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist Kind von"

    @classmethod
    def reverse_name(self) -> str:
        return "ist Elternteil von"


class PersonWeistAn(VersionMixin, Relation):
    _legacy_property_id = 145
    subj_model = Person
    obj_model = Salary

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "weist an"

    @classmethod
    def reverse_name(self) -> str:
        return "wird angewiesen von"


class IstGeborenIn(VersionMixin, Relation):
    _legacy_property_id = 146
    subj_model = Person
    obj_model = Place

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist geboren in"

    @classmethod
    def reverse_name(self) -> str:
        return "ist Geburtsort von"


class IstGestorbenIn(VersionMixin, Relation):
    _legacy_property_id = 147
    subj_model = Person
    obj_model = Place

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist gestorben in"

    @classmethod
    def reverse_name(self) -> str:
        return "ist Sterbeort von"


class GingHervorAus(VersionMixin, Relation):
    _legacy_property_id = 148
    subj_model = Function
    obj_model = Function

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ging hervor aus"

    @classmethod
    def reverse_name(self) -> str:
        return "war Vorgänger von"


class IstUntergeordnet(VersionMixin, Relation):
    _legacy_property_id = 149
    subj_model = Function
    obj_model = Function

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist untergeordnet"

    @classmethod
    def reverse_name(self) -> str:
        return "hat untergeordnete Funktion"


class IstGelegenIn(VersionMixin, Relation):
    _legacy_property_id = 150
    subj_model = Institution
    obj_model = Place

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist gelegen in"

    @classmethod
    def reverse_name(self) -> str:
        return "inkludiert"


class FindetStattIn(VersionMixin, Relation):
    _legacy_property_id = 151
    subj_model = Event
    obj_model = Place

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "findet statt in"

    @classmethod
    def reverse_name(self) -> str:
        return "ist Austragungsort von"


class WirdAusbezahltAnFunction(VersionMixin, Relation):
    _legacy_property_id = 152
    subj_model = Salary
    obj_model = Function

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "wird ausbezahlt an"

    @classmethod
    def reverse_name(self) -> str:
        return "erhält"


class IstTaetigIn(VersionMixin, Relation):
    _legacy_property_id = 473
    subj_model = Person
    obj_model = Place

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist tätig in"

    @classmethod
    def reverse_name(self) -> str:
        return "ist Tätigkeitsort von"


class HaeltSichAufIn(VersionMixin, Relation):
    _legacy_property_id = 474
    subj_model = Person
    obj_model = Place

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "hält sich auf in"

    @classmethod
    def reverse_name(self) -> str:
        return "ist Aufenthaltsort von"


class IstVormundVon(VersionMixin, Relation):
    _legacy_property_id = 475
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist Vormund von"

    @classmethod
    def reverse_name(self) -> str:
        return "ist Mündel von"


class IstTaetigAn(VersionMixin, Relation):
    _legacy_property_id = 476
    subj_model = Person
    obj_model = Institution

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist tätig an"

    @classmethod
    def reverse_name(self) -> str:
        return "hat tätige Person"


class IstPfruendnerVon(VersionMixin, Relation):
    _legacy_property_id = 477
    subj_model = Person
    obj_model = Institution

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist Pfründner von"

    @classmethod
    def reverse_name(self) -> str:
        return "hat Pfründner"


class AusgeuebtIn(VersionMixin, Relation):
    _legacy_property_id = 478
    subj_model = Function
    obj_model = Place

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ausgeübt in"

    @classmethod
    def reverse_name(self) -> str:
        return "ist Ausübungsort von"


class IstImDienstVon(VersionMixin, Relation):
    _legacy_property_id = 1978
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist im Dienst von"

    @classmethod
    def reverse_name(self) -> str:
        return "beschäftigt"


class HatHeimatortIn(VersionMixin, Relation):
    _legacy_property_id = 2421
    subj_model = Person
    obj_model = Place

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "hat Heimatort in"

    @classmethod
    def reverse_name(self) -> str:
        return "ist Heimatort von"


class IstVerpfaendetAn(VersionMixin, Relation):
    _legacy_property_id = 2422
    subj_model = Institution
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist verpfändet an"

    @classmethod
    def reverse_name(self) -> str:
        return "besitzt als Pfand"


class GehoertZu(VersionMixin, Relation):
    _legacy_property_id = 2423
    subj_model = Institution
    obj_model = Institution

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "gehört zu"

    @classmethod
    def reverse_name(self) -> str:
        return "zuständig für"


class InstitutionWeistAn(VersionMixin, Relation):
    _legacy_property_id = 2424
    subj_model = Institution
    obj_model = Salary

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "weist an"

    @classmethod
    def reverse_name(self) -> str:
        return "wird angewiesen von"


class WirdAngewiesenVon(VersionMixin, Relation):
    _legacy_property_id = 2425
    subj_model = Salary
    obj_model = Function

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "wird angewiesen von"

    @classmethod
    def reverse_name(self) -> str:
        return "weist an"


class VerkauftBesitzAn(VersionMixin, Relation):
    _legacy_property_id = 2455
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "verkauft Besitz an"

    @classmethod
    def reverse_name(self) -> str:
        return "kauft Besitz von"


class HatStreitMit(VersionMixin, Relation):
    _legacy_property_id = 2456
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "hat Streit mit"

    @classmethod
    def reverse_name(self) -> str:
        return "hat Streit mit"


class FuehrtDurch(VersionMixin, Relation):
    _legacy_property_id = 3760
    subj_model = Person
    obj_model = Salary

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "führt durch"

    @classmethod
    def reverse_name(self) -> str:
        return "wird durchgeführt von"


class FunktionFuehrtDurch(VersionMixin, Relation):
    subj_model = Function
    obj_model = Salary

    class Meta:
        ordering = ["pk"]

    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    @classmethod
    def name(self) -> str:
        return "führt durch"

    @classmethod
    def reverse_name(self) -> str:
        return "wird durchgeführt von"


class NimmtEntgegen(VersionMixin, Relation):
    _legacy_property_id = 3761
    subj_model = Person
    obj_model = Salary

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "nimmt entgegen"

    @classmethod
    def reverse_name(self) -> str:
        return "wird entgegengenommen von"


class FunktionNimmtEntgegen(VersionMixin, Relation):
    subj_model = Function
    obj_model = Salary

    class Meta:
        ordering = ["pk"]

    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    @classmethod
    def name(self) -> str:
        return "nimmt entgegen"

    @classmethod
    def reverse_name(self) -> str:
        return "wird entgegengenommen von"


class BuergtFuer(VersionMixin, Relation):
    _legacy_property_id = 4290
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "bürgt für"

    @classmethod
    def reverse_name(self) -> str:
        return "hat als Bürgen"


class IstMoeglicherweiseIdentischMit(VersionMixin, Relation):
    _legacy_property_id = 4578
    subj_model = Person
    obj_model = Person

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist möglicherweise identisch mit"

    @classmethod
    def reverse_name(self) -> str:
        return "ist möglicherweise identisch mit"


class StehtInVerbindungMit(VersionMixin, Relation):
    _legacy_property_id = 6846
    subj_model = Institution
    obj_model = Institution

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "steht in Verbindung mit"

    @classmethod
    def reverse_name(self) -> str:
        return "steht in Verbindung mit"


class IstVerbundenMit(VersionMixin, Relation):
    _legacy_property_id = 6861
    subj_model = Function
    obj_model = Function

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist verbunden mit"

    @classmethod
    def reverse_name(self) -> str:
        return "ist verbunden mit"


class IstMoeglicherweiseSpezifiziertAls(VersionMixin, Relation):
    _legacy_property_id = 6865
    subj_model = Function
    obj_model = Function

    legacy_relation_id = models.IntegerField(null=True, blank=True, editable=False)
    start = FuzzyDateParserField(null=True, blank=True)
    end = FuzzyDateParserField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pk"]

    @classmethod
    def name(self) -> str:
        return "ist möglicherweise spezifiziert als"

    @classmethod
    def reverse_name(self) -> str:
        return "ist möglicherweise verallgemeinert als"

