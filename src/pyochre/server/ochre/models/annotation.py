import logging
from django.db.models import ForeignKey, PositiveIntegerField, ManyToManyField, CASCADE
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from pyochre.server.ochre.models import OchreModel, AsyncMixin, MachineLearningModel, PrimarySource
from pyochre.utils import rdf_store
import rdflib


logger = logging.getLogger(__name__)


class Annotation(AsyncMixin, OchreModel):
    # source_type = ForeignKey(
    #     ContentType,
    #     on_delete=CASCADE,
    #     null=True,
    #     blank=True,
    #     editable=False
    # )
    # source_id = PositiveIntegerField(null=True, blank=True, editable=False)
    # source_object = GenericForeignKey('source_type', 'source_id')
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
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)
        g = rdflib.Graph()
        for tr in ds.triples((None, None, None, self.uri)):
            g.add(tr)
        return g #.serialize(format="json-ld")

    
    def delete(self, **argd):
        try:
            self.clear()
        except:
            pass
        return super(Annotation, self).delete(**argd)
    
    def save(self, *argv, **argd):
        retval = super(Annotation, self).save()
        if "annotation_graph" in argd:
            self.clear()
            store = rdf_store(settings=settings)
            ds = rdflib.Dataset(store=store)
            g = ds.graph(self.uri)
            g.parse(
                data=argd["annotation_graph"].serialize(format="turtle"),
                format="turtle"
            )
            store.commit()
        return retval
