import io
import logging
import os.path
from django.db.models import ForeignKey, PositiveIntegerField, ManyToManyField, CASCADE, SET_NULL
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from pyochre.server.ochre.models import OchreModel, AsyncMixin, MachineLearningModel, PrimarySource, Query
from pyochre.utils import rdf_store
from pyochre.utils import rdf_store, to_graph, from_graph, ochrequery as OQ
import requests
import rdflib
from rdflib.query import Result


logger = logging.getLogger(__name__)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


@shared_task
def clear(pk, uris):
    store = rdf_store(settings=settings)
    ds = rdflib.Dataset(store=store)
    for uri in uris:
        ds.remove_graph(uri)
    ds.commit()        


class Annotation(AsyncMixin, OchreModel):

    class Meta(OchreModel.Meta):
        pass    

    machinelearningmodel = ForeignKey(
        MachineLearningModel,
        null=True,
        on_delete=CASCADE,
        editable=False
    )

    primarysource = ForeignKey(
        PrimarySource,
        null=True,
        on_delete=CASCADE,
        editable=False
    )

    user = ForeignKey(
        "ochre.User",
        null=True,
        on_delete=CASCADE,
        editable=False,
        related_name="annotator"
    )
    
    @property
    def uri(self):
        return "{}{}_annotation".format(settings.OCHRE_NAMESPACE, self.id)

    def clear(self):
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)
        ds.remove_graph(self.uri)
        ds.commit()
        return None

    @property
    def annotations(self):
        resp = requests.get(
            "{}/ochre/data".format(settings.JENA_URL),
            params={"graph" : self.uri},
            headers={"Accept" : "text/turtle", "charset" : "utf-8"}
        )
        return resp.content
        # store = rdf_store(settings=settings)
        # ds = rdflib.Dataset(store=store)
        # g = rdflib.Graph()
        # for tr in ds.triples((None, None, None, self.uri)):
        #     g.add(tr)
        # return g #.serialize(format="json-ld")

    
    def delete(self, **argd):        
        clear.delay(self.id, [self.uri])
        return super(Annotation, self).delete(**argd)
    
    def save(self, *argv, **argd):
        retval = super(Annotation, self).save()
        if "annotation_graph" in argd:
            self.clear()
            resp = requests.put(
                "{}/ochre/data".format(settings.JENA_URL),
                params={"graph" : self.uri},
                data=argd["annotation_graph"],
                headers={"Content-type" : "text/turtle"}
            )
        return retval

    def query_schema(self, query):
        resp = requests.post(
            os.path.join(settings.JENA_URL, "ochre", "query"),
            data=OQ(query),
            headers={
                "Content-Type" : "application/sparql-query",
                "Accept" : "application/sparql-results+xml",
                "charset" : "utf-8"
            },
            params={
                "default-graph-uri" : [
                    self.uri,
                    self.machinelearningmodel.signature_uri if self.machinelearningmodel else "default",
                    settings.ONTOLOGY_URI
                ]
            }
        )
        return Result.parse(
            source=io.StringIO(
                resp.content.decode("utf-8")
            )
        )
    
