from apis_core.generic.signals import post_merge_with
from apis_core.apis_metainfo.signals import post_duplicate

from django.dispatch import receiver
#from django.db.models.signals import m2m_changed
from django.contrib.contenttypes.models import ContentType

from apis_bibsonomy.models import Reference
#from apis_core.apis_metainfo.models import Collection

import logging

logger = logging.getLogger(__name__)


@receiver(post_merge_with)
def merge_references(sender, instance, entities, **kwargs):
    for entity in entities:
        logger.info(f"Moving references from {entity} to {instance}")
        references = Reference.objects.filter(content_type=entity.self_contenttype, object_id=entity.id).update(object_id=instance.id)


@receiver(post_duplicate)
def copy_references(sender, instance, duplicate, **kwargs):
    logger.info(f"Copying references from {instance} to {duplicate}")
    content_type = ContentType.objects.get_for_model(instance)
    for ref in Reference.objects.filter(content_type=content_type, object_id=instance.id):
        ref.pk = None
        ref._state.adding = True
        ref.object_id = duplicate.id
        ref.save()


#@receiver(m2m_changed)
#def add_to_public_collection(sender, instance, action, reverse, model, **kwargs):
#    if action == "post_add":
#        logger.info("Adding {instance} to `published` collection")
#        try:
#            collection = Collection.objects.get(name="published")
#            modelname = instance._meta.model.__name__.lower()
#            if cset := getattr(collection, f"{modelname}_set"):
#                cset.add(instance)
#        except Collection.DoesNotExist:
#            pass


@receiver(post_merge_with)
def create_merge_metadata(sender, instance, entities, **kwargs):
    for entity in entities:
        md = instance.metadata or {}
        entstr = f"{entity.name}, {entity.first_name} (ID: {entity.id})"
        if "Legacy name (merge)" in md:
            md["Legacy name (merge)"].append(entstr)
        else:
            md["Legacy name (merge)"] = [entstr]
        instance.metadata = md
        instance.save()
