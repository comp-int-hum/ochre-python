import os.path
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib.plugins.stores.berkeleydb import BerkeleyDB
from rdflib.plugins.stores.memory import Memory


def rdf_store(
        dataset_name="ochre",
        url=None,
        path=None,
        return_format="json",
        auth=None,
        autocommit=True,
        settings=None
):
    if settings and settings.USE_JENA:
        url = settings.JENA_URL
        auth = (settings.JENA_USER, settings.JENA_PASSWORD)
    elif settings and not settings.USE_JENA:
        path = os.path.join(settings.RDF_ROOT, "rdf.bbdb")
    if url:
        store = SPARQLUpdateStore(
            query_endpoint="{}/{}/query".format(
                url,
                dataset_name
            ),
            update_endpoint="{}/{}/update".format(
                url,
                dataset_name
            ),
            autocommit=autocommit,
            returnFormat=return_format,
            auth=auth            
        )
    else:
        store = Memory()    
    return store
