import re
import json
import logging
import pickle
import gensim
import rdflib
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, Namespace
from ts.torch_handler.base_handler import BaseHandler
from pyochre.server.ochre import settings


logging.basicConfig(level=logging.INFO)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


class Handler(BaseHandler):
    
    def initialize(self, context):
        self.query = "PREFIX ochre: <{}>\n".format(settings.OCHRE_NAMESPACE) + context.manifest["model"]["modelInputSignature"]
        with open(
                context.manifest["model"]["serializedFile"],
                "rb"
        ) as ifd:
            _, self.model, _ = pickle.loads(ifd.read())

    def graph():
        pass

    def query():
        pass

    def generator():
        pass

    def singleton():
        pass
            
    def handle(self, data, context):
        retval = []
        word2id = {v : k for k, v in self.model.id2word.items()}        
        for batch in data:
            if "data" in batch:
                tokens = []
                proc_tokens = []
                known_tokens = []
                for word in batch["data"].decode("utf-8").split(" "):
                    tokens.append(word)
                    word = re.sub(r"^[^a-zA-Z0-9]+", "", word)
                    word = re.sub(r"[^a-zA-Z0-9]+$", "", word)
                    word = word.lower()
                    proc_tokens.append(word if word in word2id else None)
                known_tokens = [t for t in proc_tokens if t != None]
                if len(known_tokens) == 0:
                    topic_seq = [None for _ in tokens]
                else:
                    word_topics = {
                        self.model.id2word[wid] : None if len(topics) == 0 else topics[0] for wid, topics in self.model.get_document_topics(
                            self.model.id2word.doc2bow(known_tokens),
                            per_word_topics=True
                        )[1]
                    }
                    topic_seq = [word_topics.get(w, None) for w in proc_tokens]
                rv = []
                for t, tp in zip(tokens, topic_seq):
                    v = {"token" : t}
                    if tp != None:
                        v["label"] = tp
                    rv.append(v)
                retval.append(rv)
            elif "data_graph" in batch:
                data_graph = Graph()
                data_graph.parse(
                   data=batch["data_graph"],
                   format="turtle"
                )
                domain_graph = Graph()
                if "domain_graph" in batch:                
                    domain_graph.parse(
                        data=batch["domain_graph"],
                        format="turtle"
                    )
                doc_words = {}
                doc_tok_ids = {}
                
                tok2word = {}
                #print(self.query)
                #print(data_graph.serialize(format="turtle"))
                for s, p, o in data_graph.query(self.query):
                    if p == OCHRE["hasPart"]:
                        doc = s
                        tok = o
                        doc_tok_ids[doc] = doc_tok_ids.get(doc, [])
                        doc_tok_ids[doc].append(tok)
                    elif p == OCHRE["hasLabel"]:
                        tok = s
                        word = o
                        word = re.sub(r"^[^a-zA-Z0-9]+", "", word)
                        word = re.sub(r"[^a-zA-Z0-9]+$", "", word)
                        word = word.lower()
                        if word in word2id:
                            tok2word[tok] = word
                doc_words = {k : [tok2word.get(t, None) for t in v] for k, v in doc_tok_ids.items()}
                doc_topics = {}
                for i, (doc_id, words) in enumerate(doc_words.items()):
                    logging.info("Processing document #%d", i)
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
                for doc_id, topics in doc_topics.items():
                    assert len(topics) == len(doc_tok_ids[doc_id])
                    for tok, topic in zip(doc_tok_ids[doc_id], topics):
                        if topic != None:
                            #g.add((doc_id, OCHRE["hasPart"], tok))
                            g.add((tok, OCHRE["hasValue"], Literal(topic)))
                retval.append(
                    {
                        "output_graph" : g.serialize(format="turtle")
                    }
                )
        #for i in retval:
        #    print(list(i.keys()))
        return retval


if __name__ == "__main__":
    from importlib.resources import files
    from zipfile import ZipFile
    import pickle
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mar_file", dest="mar_file")
    parser.add_argument("--rdf_file", dest="rdf_file")
    args = parser.parse_args()
    
    #g = Graph()
    #with open(args.rdf_file, "rb") as ifd:
    #    g.parse(source=ifd, format="turtle")
        
    h = Handler()

    with ZipFile(args.mar_file, "r") as zfd:
        with zfd.open("model.bin", "r") as ifd:
            _, h.model, _ = pickle.loads(ifd.read())       

    h.query = "PREFIX ochre: <{}>\n".format(
        settings.OCHRE_NAMESPACE
    ) + files("pyochre.data").joinpath(
        "topic_model_input_signature.sparql"
    ).read_text()

    
    
    res = h.handle(
        [
            {
                "data" : "this is a test melodye" #g.serialize(format="turtle")
            }
        ],
        {}
    )
    print(res)
