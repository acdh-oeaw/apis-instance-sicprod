from apis_core.apis_entities.signals import post_merge_with
from apis_core.apis_metainfo.signals import post_duplicate

from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.contrib.contenttypes.models import ContentType

from apis_bibsonomy.models import Reference
from apis_core.apis_metainfo.models import Collection
from apis_core.apis_entities.models import TempEntityClass

import logging

logger = logging.getLogger(__name__)


@receiver(post_merge_with)
def merge_references(sender, instance, entities, **kwargs):
    for entity in entities:
        logger.info("Moving references from {entity} to {instance}")
        references = Reference.objects.filter(content_type=entity.self_contenttype, object_id=entity.id).update(object_id=instance.id)


@receiver(post_duplicate)
def copy_references(sender, instance, duplicate, **kwargs):
    logger.info("Copying references from {instance} to {duplicate}")
    content_type = ContentType.objects.get_for_model(instance)
    for ref in Reference.objects.filter(content_type=content_type, object_id=instance.id):
        ref.pk = None
        ref._state.adding = True
        ref.object_id = duplicate.id
        ref.save()


@receiver(m2m_changed, sender=TempEntityClass.collection.through)
def add_to_public_collection(sender, instance, action, **kwargs):
    if action == "post_add":
        if isinstance(instance, TempEntityClass):
            logger.info("Adding {instance} to `published` collection")
            try:
                collection = Collection.objects.get(name="published")
                collection.tempentityclass_set.add(instance)
            except Collection.DoesNotExist:
                pass
