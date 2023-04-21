import os.path
import zipfile
import pickle
import json
import random
import subprocess
import shlex
from datasets import load_dataset
import transformers
from transformers import AutoModel, AutoProcessor, AutoTokenizer, AutoConfig, AutoFeatureExtractor, AutoImageProcessor, AutoBackbone, WhisperForConditionalGeneration, WhisperProcessor
from rdflib import Dataset, Namespace
from rdflib.term import BNode, URIRef, Literal
from rdflib.namespace import RDF, SH
from rdflib.plugins.stores.sparqlstore import SPARQLConnector, SPARQLUpdateStore, SPARQLStore
from rdflib.plugins.stores.memory import Memory as MemoryStore
import torch
import torchaudio
import gensim
from gensim.models import LdaModel
from gensim.corpora import Dictionary

from gensim.models.callbacks import Metric
import sys
from pyochre.utils import rdf_store


def create_huggingface_mar(fname, model_name, ochre_path, handler_file):
    hf_org, hf_name = model_name.split("/")
    hf_url = "https://huggingface.co/{}/{}".format(hf_org, hf_name)
    base_path = os.path.join(
        ochre_path,
        "temp",
        "huggingface_repos",
        hf_org
    )
    os.makedirs(base_path, exist_ok=True)    
    repo_path = os.path.join(base_path, hf_name)

    if not os.path.exists(repo_path):
        pid = subprocess.Popen(
            shlex.split("git clone {}".format(hf_url)),
            cwd=base_path
        )
        pid.communicate()

    with open(os.path.join(repo_path, "config.json"), "rt") as ifd:
        config = json.loads(ifd.read())
    assert len(config["architectures"]) == 1
    arch_name = config["architectures"][0]
    model = getattr(transformers, arch_name).from_pretrained(repo_path)
    processor = AutoProcessor.from_pretrained(repo_path)
    #print(config)
    #p = WhisperProcessor.from_pretrained(repo_path)
    #t = AutoTokenizer.from_pretrained(repo_path)
    #z = "this is a test"
    #print(z)
    #a = processor(z, return_tensors="pt")
    #print(a)
    #b = model.generate(**a, max_length=50, do_sample=True, top_p=0.95, top_k=50) #.logits
    #print(type(b))
    #print(b)
    #print(b.squeeze(0).argmax(1))
    #print(proc.decode(b[0]))
    #print(proc.decode(a["input_ids"][0]))
    
    meta = {
        "runtime" : "python",
        "modelServerVersion": "1.0",
        "implementationVersion": "1.0",
        "specificationVersion": "1.0",
        "model": {
            "modelName": model_name,
            "serializedFile": "model.bin",
            "handler": "handler.py",
            "modelFile": "model.py",
            "modelVersion": "1.0"
        }
    }


    with open(handler_file, "rt") as ifd:
        handler = ifd.read()
    with zipfile.ZipFile(fname, "w") as zfd:
        with zfd.open("MAR-INF/MANIFEST.json", "w") as ofd:
            ofd.write(json.dumps(meta).encode())
        with zfd.open("model.bin", "w") as ofd:
            ofd.write(pickle.dumps((model, processor)))
        with zfd.open("model.py", "w") as ofd:
            ofd.write(b"class Model(object):\n    pass")
        with zfd.open("handler.py", "w") as ofd:
            ofd.write(handler.encode())

    #c = AutoConfig.from_pretrained(repo_path)
    #f = AutoFeatureExtractor.from_pretrained(repo_path)
    #ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")

    # ### AUDIO
    # audio, freq = torchaudio.load("/home/tom/recording.flac")
    # transf = torchaudio.transforms.Resample(freq, 16000)
    # taudio = transf(audio).mean(axis=0)

    # inp = proc(
    #     taudio,
    #     sampling_rate=16000,
    #     return_tensors="pt"
    # ).input_features


    # generated_ids = model.generate(inputs=inp, max_new_tokens=1000)
    # transcription = proc.batch_decode(generated_ids, skip_special_tokens=True)[0]
    # print(transcription)


    #outp = m(inp, decoder_input_ids = torch.tensor([[50258]])).logits
    #predicted_ids = torch.argmax(outp, dim=-1)
    #dec = p.batch_decode(predicted_ids)
    #print(dec)
    #i = AutoImageProcessor.from_pretrained(repo_path)
    #b = AutoBackbone.from_pretrained(repo_path)





def create_mar(fname, args):
    # cmd = [
    #     "torch-model-archiver",
    #     "--model-name", args.model_name,
    #     "--version", args.model_version,
    #     "--serialized-file", "{}/pytorch_model.bin".format(path),
    #     "--handler", args.handler,
    #     "--extra-files", "{0}/config.json,{0}/special_tokens_map.json,{0}/tokenizer_config.json,{0}/tokenizer.json".format(path),
    #     "--export-path", path,
    # ]
    # logging.info("invoking '%s'", shlex.join(cmd))
    # pid = subprocess.Popen(cmd)
    # pid.communicate()
    # shutil.move("{}/{}.mar".format(path, args.model_name), args.output)
    # return args.output
    pass


    

#@shared_task
def create_topicmodel_mar(fname, query_file, topic_count, connection, tdir, name, handler_file):
    with open(handler_file, "rt") as ifd:
        handler = ifd.read()
    with open(query_file, "rt") as ifd:
        query = ifd.read()
    ps = connection.get_objects("primarysource")["results"][0]
    store = SPARQLUpdateStore(
        query_endpoint=ps["sparql_query_url"],
        update_endpoint=ps["sparql_update_url"],
        autocommit=False,
        returnFormat="json",
    )
    dataset = Dataset(store=store)
    docs = {}
    for doc, word in dataset.query(query):
        word = word.lower()
        docs[doc] = docs.get(doc, [])
        if " " in word:
            for w in word.split():
                docs[doc].append(w)
        else:            
            docs[doc].append(word)
    dictionary = Dictionary(docs.values())

    dictionary.filter_extremes(
        no_below=3,
        no_above=0.5,
        keep_n=10000
    )
    corpus = [dictionary.doc2bow(doc) for doc in docs.values()]
    model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=topic_count,
        alpha="auto",
        eta="auto",
        iterations=20,
        passes=20,
        random_state=0,
        eval_every=None,
    )

    meta = {
        "runtime" : "python",
        "modelServerVersion": "1.0",
        "implementationVersion": "1.0",
        "specificationVersion": "1.0",
        "model": {
            "modelName": name,
            "serializedFile": "model.bin",
            "handler": "handler.py",
            "modelFile": "model.py",
            "modelVersion": "1.0"
        }
    }
    with zipfile.ZipFile(fname, "w") as zfd:
        with zfd.open("MAR-INF/MANIFEST.json", "w") as ofd:
            ofd.write(json.dumps(meta).encode())
        with zfd.open("model.bin", "w") as ofd:
            ofd.write(pickle.dumps(model))
        with zfd.open("model.py", "w") as ofd:
            ofd.write(b"class Model(object):\n    pass")
        with zfd.open("handler.py", "w") as ofd:
            ofd.write(handler.encode())
    
    #model_file = os.path.join(tdir, "model.bin")
    #with open(model_file, "wb") as ofd:
    #    ofd.write(pickle.dumps(model))
    
    # cmd = [
    #     "torch-model-archiver",
    #     "--model-name", args.model_name,
    #     "--version", args.model_version,
    #     "--serialized-file", "{}/pytorch_model.bin".format(path),
    #     "--handler", args.handler,
    #     "--extra-files", "{0}/config.json,{0}/special_tokens_map.json,{0}/tokenizer_config.json,{0}/tokenizer.json".format(path),
    #     "--export-path", path,
    # ]
    # logging.info("invoking '%s'", shlex.join(cmd))
    # pid = subprocess.Popen(cmd)
    # pid.communicate()
    # shutil.move("{}/{}.mar".format(path, args.model_name), args.output)
