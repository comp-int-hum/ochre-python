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


logger = logging.getLogger(__name__)





if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


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


def create_topic_model_mar(topic_model, name, fname):
    #from importlib.resources import files
    handler_string = files("pyochre.data").joinpath("topic_model_handler.py").read_text()
    query_string = files("pyochre.data").joinpath("topic_model_input_signature.sparql").read_text()
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
            "modelInputSignature" : query_string
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
def train_topic_model(name, user_id, query_id, primarysource_id, *argv, **argd):
    from importlib.resources import files
    signature_string = "@prefix ochre: <{}> .\n".format(settings.OCHRE_NAMESPACE) + files("pyochre.data").joinpath("topic_model_signature.ttl").read_text()
    training_query_string = """PREFIX ochre: <{}>
        {}
        """.format(
            settings.OCHRE_NAMESPACE,
            files("pyochre.data").joinpath("topic_model_training_signature.sparql").read_text()
        )

    user = User.objects.get(id=user_id)
    query = Query.objects.get(id=query_id)
    primarysource = PrimarySource.objects.get(id=primarysource_id)
    random_seed = argd.get("random_seed", 0)
    maximum_documents = argd.get("maximum_documents", 40000)
    stopwords = argd.get("stopwords", [])
    maximum_context_tokens = argd.get("maximum_context_tokens", 50)
    split_pattern = argd.get("split_pattern", r"\s+")    
    token_pattern_in = argd.get("token_pattern_in", r"(\S+)")
    token_pattern_out = argd.get("token_pattern_out", r"\1")
    lowercase = argd.get("lowercase", False)
    minimum_occurrence = argd.get("minimum_occurrence", 1)
    maximum_proportion = argd.get("maximum_proportion", 1.0)
    minimum_token_length = argd.get("minimum_token_length", 1)
    maximum_vocabulary_size = argd.get("maximum_vocabulary_size", 50000)
    topic_count = int(argd.get("topic_count", 20))
    iterations = argd.get("iterations", 100)
    passes = argd.get("passes", 100)
    models = MachineLearningModel.objects.filter(name=name, created_by=user)

    if len(models) == 1:
        model = models[0]        
        model.metadata["passes"] = passes
        model.message = "Preparing training data"
    else:
        model = MachineLearningModel(
            created_by=user,
            name=name,
            message="Preparing training data",
            metadata={
                "passes" : passes
            }
        )        
    signature_graph = Graph()
    signature_graph.parse(data=signature_string)
    model.state = model.PROCESSING
    model.save()
    random.seed(random_seed)
    docs = {}
    try:        
        g = Graph()
        for s, p, o in primarysource.query(query.sparql):
            g.add((s, p, o))
        for binding in g.query(training_query_string):
            doc = str(binding.get("doc"))
            word = binding.get("word").value
            docs[doc] = docs.get(doc, [])
            word = re.sub(r"^[^a-zA-Z0-9]+", "", word)
            word = re.sub(r"[^a-zA-Z0-9]+$", "", word)
            #if len(word) >= minimum_token_length:
            word = word.lower() if lowercase else word
            if word not in stopwords and len(word) >= minimum_token_length:
                docs[doc].append(word)

        subdocs = []
        for doc in docs.values():
            while len(doc) > 0:
                subdocs.append(doc[0:maximum_context_tokens])
                doc = doc[maximum_context_tokens:]
        
        #with open("test.out", "wt") as ofd:
        #    for subdoc in subdocs:
        #        ofd.write(" ".join(subdoc) + "\n")
                
            #     if doc_id:
        #         prefix, suffix = str(doc_id).split("/")[-2:]
        #         resp = requests.get(
        #             "http://{}:{}/materials/{}/{}/".format(
        #                 settings.HOSTNAME,
        #                 settings.PORT,
        #                 prefix,
        #                 suffix
        #             ),
        #             auth=requests.auth.HTTPBasicAuth(
        #                 settings.JENA_USER,
        #                 settings.JENA_PASSWORD
        #             )
        #         )
        #         text = resp.content.decode("utf-8")
        #         text = text.lower() if lowercase else text
        #         toks = [
        #             re.sub(
        #                 token_pattern_in,
        #                 token_pattern_out,
        #                 t
        #             ) for t in re.split(split_pattern, text) if t not in stopwords]
        #         num_subdocs = round(0.5 + len(toks) / maximum_context_tokens)
        #         toks_per = int(len(toks) / num_subdocs)
        #         for i in range(num_subdocs):
        #             docs[(prefix, suffix, i)] = toks[i * toks_per : (i + 1) * toks_per]
        #     else:
        #         doc_id = binding.get("doc_id").value #result["doc_number"]["value"]
        #         word = binding.get("word").value #result["word"]["value"]
        subdocs = [gpp.remove_stopword_tokens(toks) for toks in subdocs]
        random.shuffle(subdocs)
        logger.info(
            "Loading at most %d subdocuments out of %d",
            maximum_documents,
            len(subdocs),
        )
        subdocs = subdocs[:maximum_documents]
        logger.info("Loaded %d ubdocuments", len(subdocs))
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
                mar_path
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
                g.add((word_uris[word], OCHRE["isA"], OCHRE["Word"]))
            for topic, dist in dists:
                topic_uri = BNode()
                g.add((topic_uri, OCHRE["hasOrdinal"], Literal(topic)))
                g.add((topic_uri, OCHRE["hasLabel"], Literal("Topic #{}".format(topic))))
                g.add((topic_uri, OCHRE["isA"], OCHRE["CategoricalDistribution"]))
                for word, prob in dist:
                    occ_uri = BNode()
                    g.add((occ_uri, OCHRE["hasProbability"], Literal(prob, datatype=XSD.float)))
                    g.add((occ_uri, OCHRE["partOf"], topic_uri))
                    g.add((occ_uri, OCHRE["partOf"], word_uris[word]))
                    g.add((occ_uri, OCHRE["isA"], OCHRE["Probability"]))
            with open(prop_path, "wt") as ofd:
                ofd.write(g.skolemize().serialize(format="turtle"))
            with open(mar_path, "rb") as mar, open(sig_path, "rb") as sig, open(prop_path, "rb") as prop:
                files = {
                    #"mar_file" : mar,
                    #"signature_file" : sig,
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


