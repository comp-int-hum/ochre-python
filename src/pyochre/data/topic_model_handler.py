import re
import json
import logging
import pickle
import gensim
import rdflib
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, Namespace, XSD
from ts.torch_handler.base_handler import BaseHandler
from pyochre.server.ochre import settings
import requests
from pyochre.utils import OchreHandler


logger = logging.getLogger(__name__)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


class Handler(OchreHandler):

    def handle_batch(self, query_results):
        word2id = {v : k for k, v in self.model.id2word.items()}
        g = Graph()
        doc_tok_ids = {}
        tok2word = {}
        logger.info("Processing batch")
        for binding in query_results:
            doc = binding.get("doc")
            if "token" in binding:
                tok = binding.get("token")
                word = binding.get("word").value
                word = word.lower() if self.properties.get("lowercase", False) else word
                doc_tok_ids[doc] = doc_tok_ids.get(doc, [])
                doc_tok_ids[doc].append((None, None, tok))
                if word in word2id:
                    tok2word[tok] = word
            else:
                val = None
                if binding.get("mid"):
                    resp = requests.get(
                        "{}://{}:{}/api/material/{}/".format(
                            settings.PROTOCOL,
                            settings.HOSTNAME,
                            settings.PORT,
                            binding.get("mid").value
                        ),
                        headers={"Accept" : "application/json"}
                    )
                    if resp.ok:
                        val = resp.json()["content"]
                    else:
                       logger.info(
                           "Could not find material id '%s' for document '%s'",
                           mid,
                           binding.get("mid").value,
                           binding.get("doc")
                       )
                else:
                    val = binding["value"]
                if val:
                    for m in re.finditer(self.properties["word_regex"], val):
                        word = m.group(0)
                        start = m.start()
                        end = m.end()
                        word = word.lower() if self.properties.get("lowercase", False) else word
                        doc_tok_ids[doc] = doc_tok_ids.get(doc, [])
                        tok = BNode()
                        doc_tok_ids[doc].append((start, end, tok))
                        if word in word2id:
                            tok2word[tok] = word
        doc_words = {k : [tok2word.get(t, None) for _, _, t in v] for k, v in doc_tok_ids.items()}
        doc_topics = {}
        for i, (doc_id, words) in enumerate(doc_words.items()):
            logger.info("Processing document #%d", i)
            known_words = [w for w in words if w]
            if len(known_words) == 0:
                doc_topics[doc_id] = [None for _ in words]
            else:
                word_topics = {
                    self.model.id2word[wid] : None if len(topics) == 0 else topics[0] for wid, topics in self.model.get_document_topics(
                        self.model.id2word.doc2bow(known_words),
                        per_word_topics=True
                    )[1]
                }
                doc_topics[doc_id] = [word_topics.get(w, None) for w in words]
                
        g = Graph()
        topics = {}
        for doc_id, topics in doc_topics.items():
            assert len(topics) == len(doc_tok_ids[doc_id])
            for (start, end, tok), topic in zip(doc_tok_ids[doc_id], topics):
                if topic != None:
                    g.add((tok, OCHRE["partOf"], doc_id))
                    if start and end:
                        g.add((tok, OCHRE["hasStartIndex"], Literal(start, datatype=XSD.integer)))
                        g.add((tok, OCHRE["hasEndIndex"], Literal(end, datatype=XSD.integer)))
                        g.add((tok, OCHRE["hasAnnotation"], Literal(topic, datatype=XSD.integer)))
        return g


if __name__ == "__main__":
    from importlib.resources import files
    from zipfile import ZipFile
    import pickle
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mar_file", dest="mar_file")
    parser.add_argument("--rdf_file", dest="rdf_file")
    args = parser.parse_args()
    
    h = Handler()

    with ZipFile(args.mar_file, "r") as zfd:
        with zfd.open("model.bin", "r") as ifd:
            _, h.model, _ = pickle.loads(ifd.read())       

    h.query = "PREFIX ochre: <{}>\n".format(
        settings.OCHRE_NAMESPACE
    ) + files("pyochre").joinpath(
        "data/topic_model_input_signature.sparql"
    ).read_text()
    
    res = h.handle(
        [
            {
                "data" : b"this is a test melodye"
            }
        ],
        {}
    )
    print(res)
