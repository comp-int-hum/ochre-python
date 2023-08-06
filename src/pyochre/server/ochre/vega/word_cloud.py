import logging
from django.conf import settings
from pyochre.server.ochre.vega import OchreVisualization
from rdflib.namespace import RDF, RDFS, Namespace


OCHRE = Namespace(settings.OCHRE_NAMESPACE)
#WDE = Namespace("http://www.wikidata.org/entity/")
#WDP = Namespace("http://www.wikidata.org/prop/direct/")

logger = logging.getLogger(__name__)


class WordCloud(OchreVisualization):
    def __init__(self, object, props={}, prefix=None):
        by_cloud = {}
        max_items = 100
        value_property = OCHRE["hasProbability"]
        cloud_type = OCHRE["CategoricalDistribution"]
        item_type = OCHRE["Word"]
        for binding in object.query_properties(
            """
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX wde: <http://www.wikidata.org/entity/>
            PREFIX wdp: <http://www.wikidata.org/prop/direct/>

            SELECT ?cloud_name ?item_name ?val WHERE {{
              ?prob <{value_property}> ?val .
              ?prob ochre:partOf ?cloud .
              ?prob ochre:partOf ?item .
              ?cloud ochre:instanceOf <{cloud_type}> .
              ?item ochre:instanceOf <{item_type}> .
              ?cloud ochre:hasLabel ?cloud_name .
              ?item ochre:hasLabel ?item_name .
            }}
            """.format(
                value_property=value_property,
                cloud_type=cloud_type,
                item_type=item_type
            )
    ):
            cloud = binding.get("cloud_name")
            item = binding.get("item_name")
            probability = float(binding.get("val"))
            by_cloud[cloud] = by_cloud.get(cloud, [])
            by_cloud[cloud].append(
                {
                    "topic" : cloud,
                    "word" : item,
                    "probability" : probability
                }
            )
        self.values = []            
        for k, v in by_cloud.items():
            self.values += sorted(v, reverse=True, key=lambda x : x["probability"])[:max_items]
        super(WordCloud, self).__init__()

    @property
    def background(self):
        return {"value": "blue"}

    @property
    def scales(self):
        return [
            {
                "name": "groupy",
                "type": "band",
                "domain": {"data": "words", "field": "topic"},
                "range": {"step": {"signal" : "cellHeight"}}
            },
            {
                "name": "cscale",
                "type": "ordinal",
                "range": {"scheme": "category20"},
                "domain": {"data": "words", "field": "topic"}
            },
        ]

    @property
    def signals(self):
        return [
            {"name": "width", "value": 400},
            {"name": "cellHeight", "value": 300},
            {"name": "cellWidth", "value": 400},
            {"name": "height", "update": "domain('groupy') * cellHeight"},
        ]

    @property
    def data(self):
        return [
            {
                "name": "words",
                "values": self.values,
                "transform": [
                    {
                        "type": "formula", "as": "angle",
                        "expr": "[-45, 0, 45][~~(random() * 3)]"
                    },
                    {
                        "type": "formula", "as": "size",
                        "expr": "round(datum.value * 200)"
                    }
                ]
            }
        ]

    @property
    def marks(self):
        return [
            {
                "type": "group",
                "from": {
                    "facet": {
                        "name": "facet",
                        "data": "words",
                        "groupby": "topic",
                    }
                },
                "encode": {
                    "update": {
                        "y": {"scale": "groupy", "field": "topic"},
                        "fill": {"value": "blue"},
                        "stroke": {"value": "blue"},
                    },
                },
                "marks": [
                    {
                        "type": "text",
                        "from": {"data": "facet"},
                        "encode": {
                            "enter": {
                                "text": {"signal": "datum.word"},
                                "align": {"value": "center"},
                                "baseline": {"value": "alphabetic"},
                                "fill": {"scale": "cscale", "field": "topic"},
                            },
                            "update": {
                            }
                        },
                        "transform": [
                            {
                                "type": "wordcloud",
                                "size": [{"signal": "cellWidth"}, {"signal": "cellHeight"}],
                                "rotate": {"field": "datum.angle"},
                                "font": "Helvetica Neue, Arial",
                                "fontSize": {"field": "datum.probability"},
                                "fontSizeRange": [12, 56],
                                "padding": 2
                            }
                        ],
                    }
                ]
            },
        ]
