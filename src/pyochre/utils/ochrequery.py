import re
from django.conf import settings

def ochrequery(query, graphs=[]):
    return "PREFIX ochre: <{}>\n".format(settings.OCHRE_NAMESPACE) + query
