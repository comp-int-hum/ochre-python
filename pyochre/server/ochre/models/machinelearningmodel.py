import logging
import os.path
from django.conf import settings
import requests
import rdflib
from pyochre.server.ochre.models import OchreModel, AsyncMixin
from pyochre.utils import rdf_store


logger = logging.getLogger(__name__)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


class MachineLearningModel(AsyncMixin, OchreModel):
    
    @property
    def info(self, *argv, **argd):
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)
        g = rdflib.Graph()
        for tr in list(ds.triples((None, None, None, self.model_uri))):
            g.add(tr)
        return g

    @property
    def model_uri(self):
        return "{}{}_model".format(settings.OCHRE_NAMESPACE, self.id)
    
    def apply(self, *argv, **argd):
        response = requests.post(
            "{}/v2/models/{}/infer".format(
                settings.TORCHSERVE_INFERENCE_ADDRESS,
                self.id
            ),
            files={k : v[0] if isinstance(v, list) else v for k, v in argd.items()}
        )
        return response.content
    
    def clear(self):
        store = rdf_store(settings=settings)
        ds = rdflib.Dataset(store=store)        
        ds.remove_graph(self.model_uri)
        ds.commit()
        return None

    def delete(self, **argd):
        try:
            self.clear()
            resp = requests.delete(
                "{}/models/{}".format(
                    settings.TORCHSERVE_MANAGEMENT_ADDRESS,
                    self.id
                )
            )
        except:
            pass
        return super(MachineLearningModel, self).delete(**argd)
    
    def save(self, **argd):
        create = not (self.id and True)
        self.state = self.COMPLETE
        retval = super(MachineLearningModel, self).save()
        if "signature_file" in argd:
            self.clear()
            store = rdf_store(settings=settings)
            ds = rdflib.Dataset(store=store)
            g = ds.graph(self.model_uri)
            g.parse(source=argd["signature_file"])
            store.commit()
        elif "signature_url" in argd:
            self.clear()
            resp = requests.get(argd["signature_url"])
            store = rdf_store(settings=settings)
            ds = rdflib.Dataset(store=store)
            g = ds.graph(self.model_uri)
            g.parse(data=argd["signature_file"], format="turtle")
            store.commit()            
        if create and "mar_url" in argd:
            task = load_model.delay(self.id, argd["mar_url"])
        elif create and "mar_file" in argd:
            mname = os.path.join(settings.MODELS_ROOT, "{}_model.mar".format(self.id))
            with open(mname, "wb") as ofd:
                ofd.write(argd["mar_file"].read())
            task = load_model.delay(self.id, os.path.basename(mname))
        return retval


@shared_task
def load_model(obj_id, mar_url, *argv, **argd):
    obj = MachineLearningModel.objects.get(id=obj_id)
    obj.state = obj.PROCESSING
    resp = requests.post(
        "{}/models".format(settings.TORCHSERVE_MANAGEMENT_ADDRESS),
        params={
            "model_name" : obj.id,
            "url" : mar_url,
            "initial_workers" : 1,
        },
    )
    obj.state = obj.COMPLETE
