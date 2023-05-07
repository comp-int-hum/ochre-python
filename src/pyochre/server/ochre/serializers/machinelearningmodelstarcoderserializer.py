import logging
from rest_framework.serializers import CharField, IntegerField, HyperlinkedRelatedField, ListField, FloatField, BooleanField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import ActionOrInterfaceField
from pyochre.server.ochre.models import MachineLearningModel, Query, PrimarySource
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


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


logger = logging.getLogger(__name__)


@shared_task
def create_starcoder_model(
        model_id,
        primarysource_id,
        query_id=None,
        **argd
):
    print("TODO!")
    return None


class MachineLearningModelStarcoderSerializer(OchreSerializer):
    primarysource = HyperlinkedRelatedField(
        queryset=PrimarySource.objects.all(),
        view_name="api:primarysource-detail",
    )
    query = HyperlinkedRelatedField(
        queryset=Query.objects.all(),
        view_name="api:query-detail",
        allow_null=True,
        required=False
    )    
    class Meta:
        model = MachineLearningModel
        fields = [
            "name",
            "primarysource",
            "query",
            "url",
            "created_by",
            "id"
        ]
        
    def create(self, validated_data):
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
        create_starcoder_model.delay(
            model.id,
            **args
        )
