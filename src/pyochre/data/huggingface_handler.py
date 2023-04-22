from ts.torch_handler.base_handler import BaseHandler
import subprocess
import os.path
import base64
import io
import torchaudio
import pickle
import gensim
import rdflib
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, Namespace
import tempfile
from pyochre.server.ochre import settings
from PIL import Image
import torch
from transformers import pipeline

OCHRE = Namespace(settings.OCHRE_NAMESPACE)


class Handler(BaseHandler):
    
    def initialize(self, context):
        torchaudio.utils.sox_utils.set_buffer_size(8192 * 20)
        with open(context.manifest["model"]["serializedFile"], "rb") as ifd:
            self.processor, self.model, self.config = pickle.loads(ifd.read())
        try:
            self.pipeline = pipeline("text-generation", model=self.model, tokenizer="EleutherAI/gpt-neo-125M")
        except:
            pass
            
    def process_text(self, document):
        return [{"token" : t} for t in self.pipeline(document.decode("utf-8"), max_new_tokens=1)[0]["generated_text"].split(" ")]
    
    def process_audio(self, ifd):
        #_, fname = tempfile.mkstemp()
        _, fname = tempfile.mkstemp(suffix=".ogg")
        try:
            with open(fname, "wb") as ofd:
                ofd.write(ifd)
            #pid = subprocess.Popen(["ffmpeg", "-i", "-", fname], stdin=subprocess.PIPE)
            #pid.communicate(ifd)
            
            #subprocess.run(["ffmpeg", "-i", fnameA, fnameB])
            audio, freq = torchaudio.load(fname)
            transf = torchaudio.transforms.Resample(freq, 16000)
            taudio = transf(audio).mean(axis=0)
            inp = self.processor(taudio, sampling_rate=16000, return_tensors="pt").input_features
            predicted_ids = self.model.generate(inp, max_new_tokens=1000)
            transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            return {"transcript" : transcription}
        except Exception as e:
            raise Exception()
        #finally:
        #    os.remove(fname)

            
    def process_image(self, ifd):
        image = Image.open(io.BytesIO(ifd))
        inp = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            
            output = self.model(**inp) #torch.unsqueeze(image, 0))
            target_sizes = torch.tensor([image.size[::-1]])
            results = self.processor.post_process_object_detection(
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
        return boxes

            
    def handle(self, data, context):
        retval = []
        for batch in data:
            if "data" in batch:
                try:
                    retval.append(self.process_image(batch["data"]))
                except:
                    try:
                        retval.append(self.process_audio(batch["data"]))
                    except:
                        retval.append(self.process_text(batch["data"]))
            elif "data_graph" in batch:
                retval.append([])
            else:
                raise Exception()
        return retval


if __name__ == "__main__":
    from importlib.resources import files
    from zipfile import ZipFile
    import pickle
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mar_file", dest="mar_file")
    parser.add_argument("--input_file", dest="input_file")
    args = parser.parse_args()
    
    h = Handler()

    with ZipFile(args.mar_file, "r") as zfd:
        with zfd.open("model.bin", "r") as ifd:
            h.processor, h.model, h.config = pickle.loads(ifd.read())
            h.pipeline = pipeline("text-generation", model=h.model, tokenizer="EleutherAI/gpt-neo-125M")#config=h.config)
            
    with open(args.input_file, "rb") as ifd:
        res = h.handle(
            [
                {"data" : ifd.read()}
            ],
            None
            )
    print(res)
