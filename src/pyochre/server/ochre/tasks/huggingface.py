import typing
import subprocess
import io
import os.path
import shlex
import json
import zipfile
import pickle
from importlib.resources import files
import transformers
from transformers.modeling_outputs import ModelOutput, Seq2SeqLMOutput
from django.conf import settings
from pyochre.server.ochre.models import MachineLearningModel
from rdflib import Graph


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


input_names = {
    "input_features" : "audio",
    "input_values" : "audio",
    "input_ids" : "text",
    "pixel_values" : "image"
}

# Seq2SeqLMOutput : whisper
# CausalLMOutputWithCrossAttentions : GPT

# AudioTranscription :: audio -> text
# ObjectDetection :: image -> [(label, bounding box, score)]
# TextGeneration :: text -> text
# OpticalCharacterRecognition :: image -> [(text, bounding box)]

@shared_task
def import_huggingface_model(name, user_id, huggingface_name):
    #create_huggingface_mar(fname, model_name, ochre_path, handler_file):
    hf_org, hf_name = huggingface_name.split("/")
    hf_url = "https://huggingface.co/{}/{}".format(hf_org, hf_name)
    base_path = os.path.join(
        settings.TEMP_ROOT,
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
    mar_fname = os.path.join(repo_path, "model.mar")
    with open(os.path.join(repo_path, "config.json"), "rt") as ifd:
        config = json.loads(ifd.read())
    assert len(config["architectures"]) == 1
    arch_name = config["architectures"][0]
    model = getattr(transformers, arch_name).from_pretrained(repo_path)
    #print(typing.get_args(
    return_type = typing.get_type_hints(model.forward).get("return")
    #print(rettype, model.main_input_name)
    #rettype = [
    #    x for x in typing.get_args(
    #        typing.get_type_hints(
    #            model.forward
    #        )["return"]
    #    ) if issubclass(x, ModelOutput)][0]
    #print(rettype)
    processor = transformers.AutoProcessor.from_pretrained(repo_path)
    meta = {
        "runtime" : "python",
        "modelServerVersion": "1.0",
        "implementationVersion": "1.0",
        "specificationVersion": "1.0",
        "model": {
            "modelName": "{}-{}".format(name, user_id),
            "serializedFile": "model.bin",
            "handler": "handler.py",
            "modelFile": "model.py",
            "modelVersion": "1.0"
        }
    }
    handler_type = input_names.get(model.main_input_name, None)
    if not handler_type:
        raise Exception("No known handler for model with main input name {} and return type {}".format(model.main_input_name, return_type))

    signature_type = "object_detection" if handler_type == "image" else "speech_transcription" if handler_type == "audio" else "generative_text" if handler_type == "text" else None
    sg = Graph()
    sg.parse(data="PREFIX ochre: <{}>\n".format(settings.OCHRE_NAMESPACE) + files("pyochre").joinpath("data/{}_signature.ttl".format(signature_type)).read_text(), format="turtle")
    signature_string = sg.skolemize().serialize(format="turtle")
    
    
    #handler = files("pyochre.data").joinpath("{}_handler.py".format(handler_type)).read_text()
    handler = files("pyochre").joinpath("data/huggingface_handler.py").read_text()
    with zipfile.ZipFile(mar_fname, "w") as zfd:
        with zfd.open("MAR-INF/MANIFEST.json", "w") as ofd:
            ofd.write(json.dumps(meta).encode())
        with zfd.open("model.bin", "w") as ofd:
            ofd.write(pickle.dumps((processor, model, config)))
        with zfd.open("model.py", "w") as ofd:
            ofd.write(b"class Model(object):\n    pass")
        with zfd.open("handler.py", "w") as ofd:
            ofd.write(handler.encode())

    with open(mar_fname, "rb") as mar:
        args = {
            "mar_file" : mar,
            "signature_file" : io.StringIO(signature_string),
            #"properties_file" : prop
        }
        #print(user_id, name)
        model = MachineLearningModel.objects.get(created_by__id=user_id, name=name)
        model.save(**args)
