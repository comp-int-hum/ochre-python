import logging
from rest_framework.serializers import CharField, IntegerField, HyperlinkedRelatedField, ListField, FloatField, BooleanField
from pyochre.server.ochre.serializers import OchreSerializer, MaterialSerializer
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
from pyochre.utils import ochrequery as OQ
from pyochre.utils import ochreturtle as OT


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


logger = logging.getLogger(__name__)


class EpochLogger(Metric):
    logger = "cdh"
    title = "epochs"
    
    def __init__(self, total, *argv, **argd):
        super(EpochLogger, self).__init__()
        self.epoch = 0
        self.total = total
        self.set_epoch()

    def set_epoch(self):
        self.epoch += 1
        #self.object.message = "On pass #{}/{}".format(self.epoch, self.total)
        #self.object.save()
        
    def get_value(self, *argv, **argd):
        self.set_epoch()
        return 0


def create_topic_model_mar(topic_model, name, fname, lowercase, word_regex, stopwords):
    #from importlib.resources import files
    handler_string = files("pyochre").joinpath("data/topic_model_handler.py").read_text()
    sig_string = files("pyochre").joinpath("data/topic_model_signature.ttl").read_text()
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
            "modelVersion": "1.0",
            "modelSignature" : sig_string,
            "properties" : {
                "lowercase" : lowercase,
                "word_regex" : word_regex,
                "stopwords" : stopwords
            }
        }
    }
    with zipfile.ZipFile(fname, "w") as zfd:
        with zfd.open("MAR-INF/MANIFEST.json", "w") as ofd:
            ofd.write(json.dumps(meta).encode())
        with zfd.open("model.bin", "w") as ofd:
            ofd.write(pickle.dumps((None, topic_model, None)))
        with zfd.open("model.py", "w") as ofd:
            ofd.write(b"class Model(object):\n    pass")
        with zfd.open("handler.py", "w") as ofd:
            ofd.write(handler_string.encode())
    

@shared_task
def train_topic_model(
        model_id,
        primarysource_id,
        created_by_id,
        name,
        topic_count,
        stopwords,
        random_seed,
        passes,
        iterations,
        lowercase,
        maximum_context_tokens,
        minimum_token_length,
        maximum_vocabulary_size,
        maximum_proportion,
        minimum_occurrence,
        maximum_documents,
        word_regex,
        query_id=None,        
        **argd
):
    from importlib.resources import files
    signature_string = OT(files("pyochre").joinpath("data/topic_model_signature.ttl").read_text())
    signature_graph = Graph()
    signature_graph.parse(data=signature_string, format="turtle")
    for binding in signature_graph.query(
            OQ(
                """
                SELECT ?q WHERE {
                  ?s ochre:instanceOf ochre:InputSignature .
                  ?s ochre:hasValue ?q .
                }
                """
            )
    ):
        input_query_string = binding["q"]

    user = User.objects.get(id=created_by_id)
    initial_query = Query.objects.get(id=query_id) if query_id else None
    primarysource = PrimarySource.objects.get(id=primarysource_id)
    model = MachineLearningModel.objects.get(id=model_id)
    if random_seed != None:
        random.seed(random_seed)
    docs = {}
    tdocs = {}
    ms = MaterialSerializer()
    try:
        for binding in primarysource.query(OQ(input_query_string)):
            if binding.get("word"):
                doc = str(binding.get("doc"))
                word = binding.get("word").value
                docs[doc] = docs.get(doc, [])
                word = word.lower() if lowercase else word
                if word not in stopwords and len(word) >= minimum_token_length:
                    docs[doc].append(word)
            else:
                doc = str(binding.get("doc"))
                mid = binding.get("mid").value
                docs[doc] = docs.get(doc, [])
                text = ms.retrieve(mid)["content"]
                for m in re.finditer(word_regex, text.decode("utf-8")):
                    word = m.group(0)
                    word = word.lower() if lowercase else word
                    if word not in stopwords and len(word) >= minimum_token_length:
                        docs[doc].append(word)
                        
        subdocs = []
        for doc in docs.values():
            while len(doc) > 0:
                subdocs.append(doc[0:maximum_context_tokens])
                doc = doc[maximum_context_tokens:]
        random.shuffle(subdocs)
        logger.info(
            "Loading at most %d subdocuments out of %d",
            maximum_documents,
            len(subdocs),
        )
        subdocs = subdocs[:maximum_documents]
        logger.info("Loaded %d subdocuments", len(subdocs))
        dictionary = Dictionary(subdocs)
        dictionary.filter_extremes(
            no_below=minimum_occurrence,
            no_above=maximum_proportion,
            keep_n=maximum_vocabulary_size,            
        )
        corpus = [dictionary.doc2bow(subdoc) for subdoc in subdocs]
        el = EpochLogger(passes)
        topic_model = LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=topic_count,
            alpha="auto",
            eta="auto",
            iterations=iterations,
            passes=passes,
            random_state=random_seed,
            eval_every=None,
            #callbacks=[el],
        )
        mar_path = os.path.join(settings.TEMP_ROOT, "model_{}.mar".format(model.id))
        sig_path = os.path.join(settings.TEMP_ROOT, "sig_{}.ttl".format(model.id))
        prop_path = os.path.join(settings.TEMP_ROOT, "prop_{}.ttl".format(model.id))
        try:
            with open(sig_path, "wt") as ofd:
                ofd.write(signature_graph.skolemize().serialize(format="turtle"))
            create_topic_model_mar(
                topic_model,
                name,
                mar_path,
                lowercase,
                word_regex,
                stopwords
            )
            with open(mar_path, "rb") as mar, open(sig_path, "rb") as sig:
                files = {
                    "mar_file" : mar,
                    "signature_file" : sig,
                }
                model.save(**files)
                
            dists = topic_model.show_topics(                
                num_topics=topic_count,
                num_words=len(dictionary.token2id),
                formatted=False
            )
            
            g = Graph()
            word_uris = {}
            for word, _ in dists[0][1]:
                word_uris[word] = BNode()
                g.add((word_uris[word], OCHRE["hasLabel"], Literal(word)))
                g.add((word_uris[word], OCHRE["instanceOf"], OCHRE["Word"]))
            for topic, dist in dists:
                topic_uri = BNode()
                g.add((topic_uri, OCHRE["hasOrdinal"], Literal(topic)))
                g.add((topic_uri, OCHRE["hasLabel"], Literal("Topic #{}".format(topic))))
                g.add((topic_uri, OCHRE["instanceOf"], OCHRE["CategoricalDistribution"]))
                for word, prob in dist:
                    occ_uri = BNode()
                    g.add((occ_uri, OCHRE["hasProbability"], Literal(prob, datatype=XSD.float)))
                    g.add((occ_uri, OCHRE["partOf"], topic_uri))
                    g.add((occ_uri, OCHRE["partOf"], word_uris[word]))
                    g.add((occ_uri, OCHRE["instanceOf"], OCHRE["Probability"]))
            with open(prop_path, "wt") as ofd:
                ofd.write(g.skolemize().serialize(format="turtle"))
            with open(mar_path, "rb") as mar, open(sig_path, "rb") as sig, open(prop_path, "rb") as prop:
                files = {
                    "properties_file" : prop
                }
                model.save(**files)
        except Exception as e:
            raise e
        finally:
            os.remove(mar_path)
            os.remove(sig_path)
            os.remove(prop_path)        
    except Exception as e:        
        model.state = model.ERROR
        model.message = "{}".format(e)
        model.delete()
        raise e
    model.state = model.COMPLETE    
    model.message = ""
    model.save()


class MachineLearningModelTopicModelSerializer(OchreSerializer):
    name = CharField(
        help_text="Name of this topic model"
    )
    primarysource = HyperlinkedRelatedField(
        queryset=PrimarySource.objects.all(),
        view_name="api:primarysource-detail",
        help_text="The primary source to train the topic model on"
    )
    query = HyperlinkedRelatedField(
        queryset=Query.objects.all(),
        view_name="api:query-detail",
        allow_null=True,
        required=False,
        help_text="Optional SPARQL query file to manipulate the primary source"
    )    
    topic_count = IntegerField(
        required=False,
        write_only=True,
        default=10,
        allow_null=True,
        help_text="The number of topics the model will infer"
    )
    stopwords = ListField(
        child=CharField(
            required=False,
            write_only=True,
            help_text="A list of words to ignore"
        ),
        default=[],
        allow_null=True,
        required=False
    )
    random_seed = IntegerField(
        required=False,
        write_only=True,
        default=0,
        allow_null=True,
        help_text="Seed for random number generator"
    )
    maximum_documents = IntegerField(
        required=False,
        write_only=True,
        allow_null=True,
        default=50000,
        help_text="Maximum number of documents to train on"
    )
    passes = IntegerField(
        required=False,
        write_only=True,
        default=100,
        allow_null=True,
        help_text="Number of training passes over corpus"
    )
    iterations = IntegerField(
        required=False,
        write_only=True,
        default=100,
        allow_null=True,
        help_text="Number of iterations for variational optimization"
    )
    maximum_context_tokens = IntegerField(
        required=False,
        write_only=True,
        allow_null=True,
        default=500,
        help_text="Maximum size of a 'context' in tokens"
    )
    lowercase = BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
        default=False,
        help_text="Convert text to lower-case"
    )
    force = BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
        default=False,
        help_text="Overwrite any existing model of the same name and creator"
    )
    minimum_token_length = IntegerField(
        required=False,
        write_only=True,
        default=3,
        allow_null=True,
        help_text="Number of iterations for variational optimization"
    )
    word_regex = CharField(
        required=False,
        write_only=True,
        default="\w+",
        allow_null=True,
        help_text="Regular expression defining what counts as a 'word', used to enumerate the tokens in a non-pre-tokenized document"
    )
    maximum_vocabulary_size = IntegerField(
        required=False,
        write_only=True,
        default=30000,
        allow_null=True,
        help_text="Number of iterations for variational optimization"
    )
    minimum_occurrence = IntegerField(
        required=False,
        write_only=True,
        default=5,
        allow_null=True,
        help_text="Number of iterations for variational optimization"
    )
    maximum_proportion = FloatField(
        required=False,
        write_only=True,
        default=0.5,
        allow_null=True,
        help_text="Number of iterations for variational optimization"
    )
    class Meta:
        model = MachineLearningModel
        fields = [
            "name",
            "primarysource",
            "force",
            "query",
            "topic_count",
            "url",
            "created_by",
            "id",
            "word_regex",
            "stopwords",
            "random_seed",
            "maximum_documents",
            "passes",
            "iterations",
            "lowercase",
            "maximum_context_tokens",
            "minimum_token_length",
            "maximum_vocabulary_size",
            "maximum_proportion",
            "minimum_occurrence"
        ]
        
    def create(self, validated_data):
        if validated_data.get("force", False):
            for existing in MachineLearningModel.objects.filter(
                    name=validated_data["name"],
                    created_by=validated_data["created_by"]
            ):
                existing.delete()
        obj = MachineLearningModel(
            created_by=validated_data["created_by"],
            name=validated_data["name"],
            message="Training topic model",
            state=MachineLearningModel.PROCESSING
        )
        obj.save()
        args = {}
        for k, v in validated_data.items():
            if isinstance(v, Model):
                args[k + "_id"] = v.id
            else:
                args[k] = v
        train_topic_model.delay(
            obj.id,
            **args
        )
        return obj
