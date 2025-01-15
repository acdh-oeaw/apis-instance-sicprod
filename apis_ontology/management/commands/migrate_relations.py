from django.core.management.base import BaseCommand

from apis_core.apis_relations.models import TempTriple

from django.contrib.contenttypes.models import ContentType
from apis_core.relations.utils import relation_content_types
from apis_bibsonomy.models import Reference


class Command(BaseCommand):
    help = "Migrate from triple to relation"

    def handle(self, *args, **options):
        rel_cts = relation_content_types()
        t_content_type = ContentType.objects.get_for_model(TempTriple)
        for t in TempTriple.objects.all():
            relation = next(filter(lambda x: x.model_class()._legacy_property_id == t.prop.id, rel_cts))
            subj_content_type = ContentType.objects.get_for_model(t.subj)
            obj_content_type = ContentType.objects.get_for_model(t.obj)
            rel, created = relation.model_class().objects.get_or_create(
                    subj_content_type=subj_content_type,
                    subj_object_id=t.subj.id,
                    obj_content_type=obj_content_type,
                    obj_object_id=t.obj.id,
                    legacy_relation_id=t.id)
            rel.skip_date_parsing = True
            rel.skip_history_when_saving = True
            rel.start = t.start_date_written
            rel.start_date_from = t.start_start_date
            rel.start_date_to = t.start_end_date
            rel.start_date_sort = t.start_date
            rel.end = t.end_date_written
            rel.end_date_from = t.end_start_date
            rel.end_date_to = t.end_end_date
            rel.end_date_sort = t.end_date
            rel.notes = t.notes
            rel.save()
            for r in Reference.objects.filter(content_type=t_content_type, object_id=t.pk):
                content_type = ContentType.objects.get_for_model(rel)
                ref, created = Reference.objects.get_or_create(content_type=content_type,
                                                               object_id=rel.id,
                                                               bibs_url=r.bibs_url,
                                                               pages_start=r.pages_start,
                                                               pages_end=r.pages_end,
                                                               bibtex=r.bibtex,
                                                               attribute=r.attribute,
                                                               last_update=r.last_update,
                                                               folio=r.folio,
                                                               notes=r.notes)
