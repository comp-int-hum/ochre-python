from django.conf import settings

def ochreturtle(ttl):
    return "@prefix ochre: <{}> .\n".format(settings.OCHRE_NAMESPACE) + ttl
