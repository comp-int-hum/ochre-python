import logging
from rest_framework.serializers import CharField, IntegerField, HyperlinkedRelatedField, ListField, FloatField, BooleanField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import ActionOrInterfaceField
from pyochre.server.ochre.models import MachineLearningModel, Query, PrimarySource
from pyochre.server.ochre.fields import MachineLearningModelInteractionField
import io
import time
import zipfile
import random
import pickle
import json
from urllib.parse import urlencode
import csv
import gzip
import os.path
import logging
import re
import os
import tarfile
import tempfile
import os.path
from importlib.resources import files
from datetime import datetime
from django.db.models import Model
from django.conf import settings
from django.core.files.base import ContentFile
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from jsonpath import JSONPath
from spacy.lang import en
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, Namespace
from gensim.models.callbacks import Metric
import gensim.parsing.preprocessing as gpp
from pyochre.server.ochre.models import MachineLearningModel, Query, PrimarySource, User
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
from rdflib import Graph
from pyochre.server.ochre.models import MachineLearningModel


logger = logging.getLogger(__name__)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


input_names = {
    "input_features" : "audio",
    "input_values" : "audio",
    "input_ids" : "text",
    "pixel_values" : "image"
}


@shared_task
def import_huggingface_model(model_id, name, created_by_id, huggingface_name):
    model = MachineLearningModel.objects.get(id=model_id)
    user = User.objects.get(id=created_by_id)
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
    return_type = typing.get_type_hints(model.forward).get("return")
    processor = transformers.AutoProcessor.from_pretrained(repo_path)
    meta = {
        "runtime" : "python",
        "modelServerVersion": "1.0",
        "implementationVersion": "1.0",
        "specificationVersion": "1.0",
        "model": {
            "modelName": "{}-{}".format(name, user.id),
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
        }
        model = MachineLearningModel.objects.get(created_by__id=user.id, name=name)
        model.state = model.COMPLETE
        model.save(**args)


class MachineLearningModelHuggingfaceSerializer(OchreSerializer):

    huggingface_name = CharField(
        required=True,
        write_only=True,
        allow_null=False,
        help_text="Name of a HuggingFace model, e.g. 'facebook/detr-resnet-50'"
    )
    force = BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
        default=False,
        help_text="Overwrite any existing model of the same name and creator"
    )
    
    class Meta:
        model = MachineLearningModel
        fields = [
            "name",
            "force",
            "huggingface_name",
            "url",
            "created_by",
            "id",
        ]
        
    def create(self, validated_data):
        if validated_data.get("force", False):
            for existing in MachineLearningModel.objects.filter(
                    name=validated_data["name"],
                    created_by=validated_data["created_by"]
            ):
                existing.delete()
        model = MachineLearningModel(
            created_by=validated_data["created_by"],
            name=validated_data["name"],
            state=MachineLearningModel.PROCESSING,
            message="Importing Huggingface model",
        )        
        model.save()
        args = {}
        for k, v in validated_data.items():
            if isinstance(v, Model):
                args[k + "_id"] = v.id
            else:
                args[k] = v
        import_huggingface_model.delay(
            model.id,
            **args
        )
