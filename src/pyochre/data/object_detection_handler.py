import logging
import io
import pickle
from PIL import Image
from ts.torch_handler.base_handler import BaseHandler
import rdflib
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, Namespace
from torchvision import transforms
import torch
from pyochre.server.ochre import settings


logging.basicConfig(level=logging.INFO)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")


class Handler(BaseHandler):
    image_processing = transforms.Compose([transforms.ToTensor()])
    threshold = 0.5
    
    def initialize(self, context):
        with open(context.manifest["model"]["serializedFile"], "rb") as ifd:
            self.preprocessor, self.model, self.postprocessor = pickle.loads(ifd.read())

    def graph():
        pass

    def query():
        pass

    def generator():
        pass

    def singleton(self, ifd):
        image = Image.open(io.BytesIO(ifd))
        inp = self.preprocessor(images=image, return_tensors="pt")
        
        with torch.no_grad():
            
            output = self.model(**inp) #torch.unsqueeze(image, 0))
            target_sizes = torch.tensor([image.size[::-1]])
            results = self.preprocessor.post_process_object_detection(
                output,
                target_sizes=target_sizes,
                threshold=0.9
            )[0]
            boxes = []
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                boxes.append(
                    {
                        self.model.config.id2label[label.item()] : [round(i, 2) for i in box.tolist()],
                        "score" : score.item()
                    }
                )

            print(boxes)
            return boxes
            
    def handle(self, data, context):
        retval = []        
        for batch in data:
            #print(list(batch.keys()))
            if batch.get("domain_graph"):
                pass

            else:
                retval.append(self.singleton(batch["file"]))
        #print(retval)
        return retval
