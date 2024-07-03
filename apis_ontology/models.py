from django.db import models
from django.contrib.contenttypes.models import ContentType
from apis_core.apis_entities.models import AbstractEntity
from apis_core.core.models import LegacyDateMixin
from apis_core.collections.models import SkosCollection, SkosCollectionContentObject
from apis_core.history.models import VersionMixin

from auditlog.registry import auditlog


class LegacyStuffMixin(models.Model):
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
        parent = SkosCollection.objects.get(name="sicprod")
        content_type = ContentType.objects.get_for_model(self)
        sccos = SkosCollectionContentObject.objects.filter(collection__parent=parent, content_type=content_type, object_id=self.pk).values_list("collection")
        return SkosCollection.objects.filter(id__in=sccos)


class Person(VersionMixin, LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    Person, eine Subklasse von crm:E21_Person.
    Generated from model xml
    """
    first_name = models.CharField(max_length=1024, blank=True, null=True, verbose_name = "Vorname", help_text = "Vorname der Person.")
    name = models.CharField(max_length=255, verbose_name="Name", blank=True)
    GENDER_CHOICES = (("männlich", "männlich"), ("weiblich", "weiblich"), ("unbekannt", "unbekannt"), )
    gender = models.CharField(max_length=9, choices=GENDER_CHOICES, blank=True, verbose_name = "Geschlecht", help_text = "Geschlecht der Person.")
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternative Namen", help_text = "Feld um alternative Namen anzugeben.")

    class Meta:
        ordering = ["name", "first_name"]

    def __str__(self):
        return "{}, {} (ID: {})".format(self.name, self.first_name, self.id)


class Function(VersionMixin, LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    Eine Funktion kann von einer Person an einer Institution oder einem Hof ausgeübt werden kann.
    Generated from model xml
    """
    name = models.CharField(max_length=255, verbose_name="Name", blank=True)
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Andere Namen für die Funktion.")

    class Meta:
        ordering = ["name"]


class Place(VersionMixin, LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    Orte in SiCProD, Subklasse von crm:E53_Place.
    Generated from model xml
    """
    name = models.CharField(max_length=255, verbose_name="Name", blank=True)
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Alternativer Name für einen Ort.")
    TYPE_CHOICES = (("Stadt", "Stadt"), ("Dorf/Nachbarschaft/Gemein/Siedlung/Weiler", "Dorf/Nachbarschaft/Gemein/Siedlung/Weiler"), ("Burg/Schloss", "Burg/Schloss"), ("Land/Herrschaftskomplex", "Land/Herrschaftskomplex"), ("Landschaft/Region", "Landschaft/Region"), ("Lehen", "Lehen"), ("Haus/Hof", "Haus/Hof"), ("Gericht", "Gericht"), ("Kloster", "Kloster"), ("Gewässer", "Gewässer"), ("Grundherrschaft", "Grundherrschaft"), ("Hofmark", "Hofmark"), ("Tal", "Tal"), ("Berg", "Berg"), ("Bergrevier", "Bergrevier"), ("Pflege", "Pflege"), ("(Land-)Vogtei", "(Land-)Vogtei"), ("Propstei", "Propstei"), )
    type = models.CharField(max_length=41, choices=TYPE_CHOICES, blank=True, verbose_name = "Typ", help_text = "Art des Ortes.")
    latitude = models.FloatField(null=True, blank=True, verbose_name = "Breitengrad", help_text = "Breitengrad des Ortes. Bei Polygonen wird die Mitte verwendet.")
    longitude = models.FloatField(null=True, blank=True, verbose_name = "Längengrad", help_text = "Längengrad des Ortes. Bei Polygonen wird die Mitte verwendet.")

    class Meta:
        ordering = ["name"]


class Institution(VersionMixin, LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    SiCProD Institution, Subklasse von crm:E74_Group. Wird für alle Institutionen benutzt die kein Hof sind
    Generated from model xml
    """
    name = models.CharField(max_length=255, verbose_name="Name", blank=True)
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Alternativer Name der Institution.")
    TYPE_CHOICES = (("Kanzlei", "Kanzlei"), ("Hofkapelle", "Hofkapelle"), ("Küche", "Küche"), ("(Dom-)Kapitel", "(Dom-)Kapitel"), ("Universität", "Universität"), ("Kloster", "Kloster"), ("Frauenzimmer", "Frauenzimmer"), ("Bistum", "Bistum"), ("Pfarrei", "Pfarrei"), )
    type = models.CharField(max_length=13, choices=TYPE_CHOICES, blank=True, verbose_name = "Typ", help_text = "Art der institution.")

    class Meta:
        ordering = ["name"]


class Event(VersionMixin, LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    SiCProD Ereignis, Subklasse von crm:E5_Event.
    Generated from model xml
    """
    name = models.CharField(max_length=255, verbose_name="Name", blank=True)
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Alternativer Name.")
    TYPE_CHOICES = (("Hochzeit", "Hochzeit"), ("Landtag", "Landtag"), ("Fest/Turnier", "Fest/Turnier"), ("Schlacht", "Schlacht"), ("Gesandtschaft/Reise", "Gesandtschaft/Reise"), ("Taufe", "Taufe"), ("Amtseinsetzung", "Amtseinsetzung"), ("Reichstag", "Reichstag"), )
    type = models.CharField(max_length=19, choices=TYPE_CHOICES, blank=True, verbose_name = "Typ", help_text = "Typ des Ereignisses.")

    class Meta:
        ordering = ["name"]


class Salary(VersionMixin, LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    Ein Gehalt ist die Menge an Geld die eine Person als Gegenleistung erhalten hat. Das Gehalt muss keine wiederkehrende Zahlung sein.
    Generated from model xml
    """
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


from apis_core.relations.models import Relation

class Bewohnt(Relation):
    class Meta:
        verbose_name = "bewohnt"
    subj_model = Person
    obj_model = Place


class Besitzt(Relation):
    class Meta:
        verbose_name = "besitzt"
    subj_model = Person
    obj_model = Place


class Hat_korrespondenz_mit(Relation):
    class Meta:
        verbose_name = "hat Korrespondenz mit"
    subj_model = Person
    obj_model = Person


class Hat_familienbeziehung_zu(Relation):
    class Meta:
        verbose_name = "hat Familienbeziehung zu"
    subj_model = Person
    obj_model = Person


class Hat_ehe_mit(Relation):
    class Meta:
        verbose_name = "hat Ehe mit"
    subj_model = Person
    obj_model = Person


class Empfiehlt(Relation):
    class Meta:
        verbose_name = "empfiehlt"
    subj_model = Person
    obj_model = Person


class Hat_geschaeftsbeziehung_zu(Relation):
    class Meta:
        verbose_name = "hat Geschäftsbeziehung zu"
    subj_model = Person
    obj_model = Person


class Ist_mitglied_von(Relation):
    class Meta:
        verbose_name = "ist Mitglied von"
    subj_model = Person
    obj_model = Institution


class Nimmt_teil_an(Relation):
    class Meta:
        verbose_name = "nimmt teil an"
    subj_model = Person
    obj_model = Event
    foo = models.ForeignKey(Person, on_delete=models.CASCADE)


class Wird_ausbezahlt_an(Relation):
    class Meta:
        verbose_name = "wird ausbezahlt an"
    subj_model = Salary
    obj_model = [Person, Function]


class Wird_ausgeuebt_von(Relation):
    class Meta:
        verbose_name = "wird ausgeübt von"
    subj_model = Function
    obj_model = Person

    @classmethod
    def reverse_name(cls):
        return "übt aus"


class Ist_teil_von(Relation):
    class Meta:
        verbose_name = "ist Teil von"
    subj_model = Place
    obj_model = Place


class Fuehrt_durch(Relation):
    class Meta:
        verbose_name = "führt durch"
    subj_model = [Institution, Function, Person]
    obj_model = Salary


class Ist_bruder_schwester_von(Relation):
    class Meta:
        verbose_name = "ist Bruder/Schwester von"
    subj_model = Person
    obj_model = Person


class Ist_kind_von(Relation):
    class Meta:
        verbose_name = "ist Kind von"
    subj_model = Person
    obj_model = Person


class Weist_an(Relation):
    class Meta:
        verbose_name = "weist an"
    subj_model = [Person, Institution]
    obj_model = Salary


class Ist_geboren_in(Relation):
    class Meta:
        verbose_name = "ist geboren in"
    subj_model = Person
    obj_model = Place


class Ist_gestorben_in(Relation):
    class Meta:
        verbose_name = "ist gestorben in"
    subj_model = Person
    obj_model = Place


class Ging_hervor_aus(Relation):
    class Meta:
        verbose_name = "ging hervor aus"
    subj_model = Function
    obj_model = Function


class Ist_untergeordnet(Relation):
    class Meta:
        verbose_name = "ist untergeordnet"
    subj_model = Function
    obj_model = Function


class Ist_gelegen_in(Relation):
    class Meta:
        verbose_name = "ist gelegen in"
    subj_model = Institution
    obj_model = Place


class Findet_statt_in(Relation):
    class Meta:
        verbose_name = "findet statt in"
    subj_model = Event
    obj_model = Place


class Ist_taetig_in(Relation):
    class Meta:
        verbose_name = "ist tätig in"
    subj_model = Person
    obj_model = Place


class Haelt_sich_auf_in(Relation):
    class Meta:
        verbose_name = "hält sich auf in"
    subj_model = Person
    obj_model = Place


class Ist_vormund_von(Relation):
    class Meta:
        verbose_name = "ist Vormund von"
    subj_model = Person
    obj_model = Person


class Ist_taetig_an(Relation):
    class Meta:
        verbose_name = "ist tätig an"
    subj_model = Person
    obj_model = Institution


class Ist_pfruendner_von(Relation):
    class Meta:
        verbose_name = "ist Pfründner von"
    subj_model = Person
    obj_model = Institution


class Ausgeuebt_in(Relation):
    class Meta:
        verbose_name = "ausgeübt in"
    subj_model = Function
    obj_model = Place


class Ist_im_dienst_von(Relation):
    class Meta:
        verbose_name = "ist im Dienst von"
    subj_model = Person
    obj_model = Person


class Hat_heimatort_in(Relation):
    class Meta:
        verbose_name = "hat Heimatort in"
    subj_model = Person
    obj_model = Place


class Ist_verpfaendet_an(Relation):
    class Meta:
        verbose_name = "ist verpfändet an"
    subj_model = Institution
    obj_model = Person


class Gehoert_zu(Relation):
    class Meta:
        verbose_name = "gehört zu"
    subj_model = Institution
    obj_model = Institution


class Wird_angewiesen_von(Relation):
    class Meta:
        verbose_name = "wird angewiesen von"
    subj_model = Salary
    obj_model = Function


class Verkauft_besitz_an(Relation):
    class Meta:
        verbose_name = "verkauft Besitz an"
    subj_model = Person
    obj_model = Person


class Hat_streit_mit(Relation):
    class Meta:
        verbose_name = "hat Streit mit"
    subj_model = Person
    obj_model = Person


class Nimmt_entgegen(Relation):
    class Meta:
        verbose_name = "nimmt entgegen"
    subj_model = [Function, Person]
    obj_model = Salary


class Buergt_fuer(Relation):
    class Meta:
        verbose_name = "bürgt für"
    subj_model = Person
    obj_model = Person


class Ist_moeglicherweise_identisch_mit(Relation):
    class Meta:
        verbose_name = "ist möglicherweise identisch mit"
    subj_model = Person
    obj_model = Person


class Steht_in_verbindung_mit(Relation):
    class Meta:
        verbose_name = "steht in Verbindung mit"
    subj_model = Institution
    obj_model = Institution


class Ist_verbunden_mit(Relation):
    class Meta:
        verbose_name = "ist verbunden mit"
    subj_model = Function
    obj_model = Function


class Ist_moeglicherweise_spezifiziert_als(Relation):
    class Meta:
        verbose_name = "ist möglicherweise spezifiziert als"
    subj_model = Function
    obj_model = Function
