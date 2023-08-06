import logging
import hashlib
import inspect
from django.core.cache import cache


logger = logging.getLogger(__name__)


def ochre_cache_method(method):
    code = inspect.getsource(method)
    def cached_method(*argv, **argd):
        obj = argv[0]
        h = hashlib.sha1()
        h.update(bytes(code, "utf-8"))
        latest_ts = None
        objs = set()
        for k, v in list(enumerate(argv)) + list(argd.items()):
            if hasattr(v, "_meta"):
                objs.add(
                    "{}_{}".format(
                        v._meta.model_name,
                        v.id
                    )
                )
                ts = v.modified_at if v.modified_at else v.created_at
                if latest_ts == None or ts > latest_ts:
                    latest_ts = ts
                h.update(bytes(str(k), "utf-8") + bytes(str(v.name), "utf-8") + bytes(str(v.created_by.username), "utf-8"))
            else:
                h.update(bytes(str(k), "utf-8") + bytes(str(v), "utf-8"))
        key = h.hexdigest()
        ts_key = "{}_ts".format(key)
        cache_ts = cache.get(ts_key)
        logger.info("Comparing %s to %s", cache_ts, latest_ts)
        if cache_ts == None or cache_ts < latest_ts:
            logger.info("cache miss for key '{}'".format(key))
            retval = method(*argv, **argd)
            cache.set(ts_key, latest_ts, timeout=None)
            cache.set(key, retval, timeout=None)
            for obj in objs:
                deps = cache.get(obj, default=set())
                deps.add(key)
                cache.set(obj, deps)
            return retval
        else:
            logger.info("cache hit for key '{}'".format(key))
            return cache.get(key)
    return cached_method
