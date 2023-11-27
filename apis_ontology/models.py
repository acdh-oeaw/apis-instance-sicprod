import reversion
from django.db import models
from apis_core.apis_entities.models import AbstractEntity
from apis_core.core.models import LegacyDateMixin


class LegacyStuffMixin(models.Model):
    review = review = models.BooleanField(default=False, help_text="Should be set to True, if the data record holds up quality standards.")
    status = models.CharField(max_length=100, blank=True)
    references = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)
    collection = models.ManyToManyField("apis_metainfo.Collection")
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        abstract = True


@reversion.register(follow=["rootobject_ptr"])
class Person(LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    Person, eine Subklasse von crm:E21_Person.
    Generated from model xml
    """
    first_name = models.CharField(max_length=1024, blank=True, null=True, verbose_name = "Vorname", help_text = "Vorname der Person.")
    GENDER_CHOICES = (("männlich", "männlich"), ("weiblich", "weiblich"), ("unbekannt", "unbekannt"), )
    gender = models.CharField(max_length=9, choices=GENDER_CHOICES, blank=True, verbose_name = "Geschlecht", help_text = "Geschlecht der Person.")
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Feld um alternative Namen anzugeben.")


@reversion.register(follow=["rootobject_ptr"])
class Function(LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    Eine Funktion kann von einer Person an einer Institution oder einem Hof ausgeübt werden kann.
    Generated from model xml
    """
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Andere Namen für die Funktion.")


@reversion.register(follow=["rootobject_ptr"])
class Place(LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    Orte in SiCProD, Subklasse von crm:E53_Place.
    Generated from model xml
    """
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Alternativer Name für einen Ort.")
    TYPE_CHOICES = (("Stadt", "Stadt"), ("Dorf/Nachbarschaft/Gemein/Siedlung/Weiler", "Dorf/Nachbarschaft/Gemein/Siedlung/Weiler"), ("Burg/Schloss", "Burg/Schloss"), ("Land/Herrschaftskomplex", "Land/Herrschaftskomplex"), ("Landschaft/Region", "Landschaft/Region"), ("Lehen", "Lehen"), ("Haus/Hof", "Haus/Hof"), ("Gericht", "Gericht"), ("Kloster", "Kloster"), ("Gewässer", "Gewässer"), ("Grundherrschaft", "Grundherrschaft"), ("Hofmark", "Hofmark"), ("Tal", "Tal"), ("Berg", "Berg"), ("Bergrevier", "Bergrevier"), ("Pflege", "Pflege"), ("(Land-)Vogtei", "(Land-)Vogtei"), ("Propstei", "Propstei"), )
    type = models.CharField(max_length=41, choices=TYPE_CHOICES, blank=True, verbose_name = "Typ", help_text = "Art des Ortes.")
    latitude = models.FloatField(null=True, blank=True, verbose_name = "Breitengrad", help_text = "Breitengrad des Ortes. Bei Polygonen wird die Mitte verwendet.")
    longitude = models.FloatField(null=True, blank=True, verbose_name = "Längengrad", help_text = "Längengrad des Ortes. Bei Polygonen wird die Mitte verwendet.")


@reversion.register(follow=["rootobject_ptr"])
class Institution(LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    SiCProD Institution, Subklasse von crm:E74_Group. Wird für alle Institutionen benutzt die kein Hof sind
    Generated from model xml
    """
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Alternativer Name der Institution.")
    TYPE_CHOICES = (("Kanzlei", "Kanzlei"), ("Hofkapelle", "Hofkapelle"), ("Küche", "Küche"), ("(Dom-)Kapitel", "(Dom-)Kapitel"), ("Universität", "Universität"), ("Kloster", "Kloster"), ("Frauenzimmer", "Frauenzimmer"), ("Bistum", "Bistum"), ("Pfarrei", "Pfarrei"), )
    type = models.CharField(max_length=13, choices=TYPE_CHOICES, blank=True, verbose_name = "Typ", help_text = "Art der institution.")


@reversion.register(follow=["rootobject_ptr"])
class Event(LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    SiCProD Ereignis, Subklasse von crm:E5_Event.
    Generated from model xml
    """
    alternative_label = models.TextField(blank=True, null=True, verbose_name = "Alternativer Name", help_text = "Alternativer Name.")
    TYPE_CHOICES = (("Hochzeit", "Hochzeit"), ("Landtag", "Landtag"), ("Fest/Turnier", "Fest/Turnier"), ("Schlacht", "Schlacht"), ("Gesandtschaft/Reise", "Gesandtschaft/Reise"), ("Taufe", "Taufe"), ("Amtseinsetzung", "Amtseinsetzung"), ("Reichstag", "Reichstag"), )
    type = models.CharField(max_length=19, choices=TYPE_CHOICES, blank=True, verbose_name = "Typ", help_text = "Typ des Ereignisses.")


@reversion.register(follow=["rootobject_ptr"])
class Salary(LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    """
    Ein Gehalt ist die Menge an Geld die eine Person als Gegenleistung erhalten hat. Das Gehalt muss keine wiederkehrende Zahlung sein.
    Generated from model xml
    """
    TYP_CHOICES = (("Sold", "Sold"), ("Zehrung", "Zehrung"), ("Provision", "Provision"), ("Kredit", "Kredit"), ("Sonstiges", "Sonstiges"), ("Burghut", "Burghut"), ("Botenlohn", "Botenlohn"), )
    typ = models.CharField(max_length=9, choices=TYP_CHOICES, blank=True, verbose_name = "Typ", help_text = "Art des Gehalts.")
    REPETITIONTYPE_CHOICES = (("einfach", "einfach"), ("wiederholend", "wiederholend"), )
    repetitionType = models.CharField(max_length=12, choices=REPETITIONTYPE_CHOICES, blank=True, verbose_name = "Typ Wiederholungen", help_text = "Typ des Gehalts.")
