import logging
import hashlib
from django.core.cache import cache


logger = logging.getLogger(__name__)


def ochre_cache_method(method):
    def cached_method(*argv, **argd):
        try:
            obj = argv[0]
            h = hashlib.sha1()
            #h.update(bytes(str((argv[1:], argd)), "utf-8"))
            uid = h.hexdigest()
            key = "{}_{}_{}_{}_{}".format(
                obj._meta.app_label,
                obj._meta.model_name,
                obj.id, method.__name__,
                uid
            )
            logger.error(str(obj) + method.__name__)
            timestamp_key = "TIMESTAMP_{}_{}_{}_{}_{}".format(
                obj._meta.app_label,
                obj._meta.model_name,
                obj.id,
                method.__name__,
                uid
            )
            cache_ts = cache.get(timestamp_key)
            obj_ts = obj.modified_at
            logger.info("Comparing %s to %s", cache_ts, obj_ts)
        except:
            retval = method(*argv, **argd)
            return retval
        if cache_ts == None or cache_ts < obj_ts:
            logger.info("cache miss for key '{}'".format(key))
            retval = method(*argv, **argd)
            cache.set(timestamp_key, obj_ts, timeout=None)
            cache.set(key, retval, timeout=None)
            return retval
        else:
            logger.info("cache hit for key '{}'".format(key))
            return cache.get(key)
    return cached_method
