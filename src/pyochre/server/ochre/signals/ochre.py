import logging
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.core.cache import cache
from guardian.shortcuts import get_anonymous_user, get_perms, get_objects_for_user, assign_perm, get_users_with_perms, get_groups_with_perms, remove_perm
from pyochre.server.ochre.models import OchreModel


logger = logging.getLogger(__name__)


@receiver(pre_delete)
def pre_delete_callback(
        sender,
        instance,
        using,
        *argv,
        **argd
):
    key = "{}_{}".format(
        instance._meta.model_name,
        instance.id
    )
    logger.info("Clearing cache entries depending on '%s'", key)
    for dep in cache.get(key, set()):
        cache.delete(dep)
    cache.delete(key)


@receiver(post_save)
def post_save_callback(
        sender,
        instance,
        created,
        raw,
        using,
        update_fields,
        *argv,
        **argd
):
    key = "{}_{}".format(
        instance._meta.model_name,
        instance.id
    )
    logger.info("Clearing cache entries depending on '%s'", key)
    for dep in cache.get(key, set()):
        cache.delete(dep)
    cache.delete(key)
    
    User = get_user_model()
    try:
        anon = get_anonymous_user()
    except:
        anon = None
    if created and isinstance(
            instance,
            (
                OchreModel,
                User
            )
    ) and anon:
        assign_perm(
            "{}.{}_{}".format(
                instance._meta.app_label,
                "view",
                instance._meta.model_name
            ),
            anon,
            instance
        )
        for perm in ["delete", "change", "view"]:
            assign_perm(
                "{}.{}_{}".format(
                    instance._meta.app_label,
                    perm,
                    instance._meta.model_name
                ),
                instance if isinstance(
                    instance,
                    get_user_model()
                ) else instance.created_by,
                instance
            )
        logger.info("Set initial permissions for %s", instance)
