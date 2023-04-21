import logging
from ts.torch_handler.base_handler import BaseHandler
import pickle
import gensim
import rdflib
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, Namespace
from pyochre.server.ochre import settings

logging.basicConfig(level=logging.INFO)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")


class Handler(BaseHandler):
    
    def initialize(self, context):
        with open(context.manifest["model"]["serializedFile"], "rb") as ifd:
            self.model = pickle.loads(ifd.read())

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
        #logging.error(str(type(data)))
        #logging.error(str(data))
        #return None
        for batch in data:
            if batch.get("domain_graph"):
                if batch.get("data_graph"):
                    retval.append(
                        self.graph(
                            json.loads(batch["domain_graph"]),
                            json.loads(batch["data_graph"])
                        )
                    )
                elif batch.get("query_results"):
                    retval.append(
                        self.query(
                            json.loads(batch["domain_graph"]),
                            json.loads(batch["query_results"])
                        )
                    )
                else:
                    retval.append(
                        self.generator(
                            json.loads(batch["domain_graph"])
                        )
                    )
            elif batch.get("singleton"):
                retval.append(self.singleton(json.loads(batch["singleton"])))
            else:
                raise Exception("Each data item the model is being applied to must either have 'singleton' or 'domain_graph' keys")
            # ig = rdflib.Graph()
            # ig.parse(data=batch["graph"])
            # tokens = [
            #     (t[0].value, t[1].value) for t in ig.query(                
            #         """
            #         PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            #         SELECT ?i ?t WHERE
            #         {
            #           ?n wdt:P2561 ?t .
            #           ?n wdt:P1545 ?i .
            #         } ORDER BY ASC(?i)
            #         """
            #     )
            # ]
            # tokens = [x[1] for x in tokens]
            # og = rdflib.Graph()
            # _, text_topics, _ = self.model.get_document_topics(
            #     self.model.id2word.doc2bow(tokens),
            #     per_word_topics=True
            # )
            # word2topic = {
            #     self.model.id2word[wid] : None if len(topics) == 0 else topics[0] for wid, topics in text_topics
            # }
            # for i, (token, topic) in enumerate(
            #         [
            #             (
            #                 token,
            #                 word2topic.get(token, None)
            #             ) for token in tokens
            #         ]
            # ):

            #     b = BNode()
            #     og.add(
            #         (
            #             b,
            #             WDT["P1545"],
            #             Literal(i)
            #         )
            #     )
            #     og.add(
            #         (
            #             b,
            #             WDT["P2561"],
            #             Literal(token)
            #         )
            #     )
            #     if topic:                    
            #         og.add(
            #             (
            #                 b,
            #                 WDT["P1269"],
            #                 Literal(str(topic))
            #             )
            #         )
            # retval.append(og.serialize(format="turtle"))
        logging.error(str(retval))
        return retval
