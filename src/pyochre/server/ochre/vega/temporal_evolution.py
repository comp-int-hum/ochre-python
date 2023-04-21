import logging
from importlib.resources import files
from django.conf import settings
from pyochre.server.ochre.vega import OchreVisualization
from pyochre.utils import rdf_store

logger = logging.getLogger(__name__)


query = "PREFIX ochre: <{}>\n".format(settings.OCHRE_NAMESPACE) + """
  SELECT ?bucket ?bucket_name ?topic (COUNT(?topic) as ?count) WHERE {
  	?story ochre:isA ochre:Story .
  	?story ochre:hasOrdinal ?bucket .
        ?story ochre:hasTag ?bucket_name .
  	?story ochre:hasPart ?line .
  	?story ochre:hasLabel ?title .
  	?line ochre:isA ochre:LineOfVerse .
  	?line ochre:hasPart ?token .
  	?token ochre:isA ochre:Token .
  	?line ochre:hasOrdinal ?line_number .
  	?token ochre:hasLabel ?word .
        ?token	ochre:hasValue ?topic .
  } GROUP BY ?bucket ?topic ?bucket_name
"""

class TemporalEvolution(OchreVisualization):

    def __init__(self, values, prefix=None):
        store = rdf_store(settings=settings)
        query_string = "PREFIX ochre: <{}>\n".format(settings.OCHRE_NAMESPACE) + files("pyochre.data").joinpath("temporal_evolution_query.sparql").read_text() % {
            "data" : values.primarysource.data_uri,
            "annotation" : values.uri
        }
        self.prefix = prefix
        self.values = []
        for binding in sorted(store.query(query_string), key=lambda x : x.get("bucket")):
            
            self.values.append(
                {
                    "bucket" : binding.get("bucket_name"),
                    "topic" : binding.get("topic"),
                    "count" : binding.get("count")
                }
            )
        #for bucket, info in sorted(values[1].items(), key=lambda x : x[0]):
        #     total = sum(info["weights"].values())
        #     for topic, count in info["weights"].items():
        #         self.values.append(
        #             {
        #                 "bucket" : bucket,
        #                 "topic" : topic,
        #                 "count" : count,
        #                 "percent" : count / total
        #             }
        #         )
        super(TemporalEvolution, self).__init__()

    @property
    def background(self):
        return "black"

    @property
    def signals(self):
        return [
            {
                "name": "width",
                "value": 800
            },
            {
                "name": "height",
                "value": 350
            },
            {
                "name" : "topic",
                "value" : "",
                "bind" : {
                    "input" : "textarea",
                    "element" : "#{}_1".format(self.prefix) if self.prefix else "#topicinfo"
                },
                "on" : [
                   {"events" : "area:mouseover", "update" : "datum.topic"},
                   {"events" : "area:mouseout", "update" : {"value" : ""}}
                ],
            },
        ]
        
    @property
    def data(self):
        return [
            {
                "name": "temporal_weights",
                "values": self.values,
                "transform": [
                    {
                        "type": "stack",
                        "field": "percent",
                        "groupby": ["bucket"],
                        "sort": {
                            "field": ["topic"],
                            "order": ["descending"]
                        }
                    },
                ]
            },
            {
                "name": "series",
                "source": "temporal_weights",
                "transform": [
                    {
                        "type": "aggregate",
                        "groupby": ["bucket"],
                        "fields": ["percent", "percent"],
                        "ops": ["sum", "argmax"],
                        "as": ["sum", "argmax"]
                    }
                ]
            }            
        ]

    @property
    def scales(self):
        return [
            {
                "name": "xscale",
                "type": "point",
                "range": "width",
                "domain": {"data": "temporal_weights", "field": "bucket"}
            },
            {
                "name": "yscale",
                "type": "linear",
                "range": "height",
                "nice": True,
                "zero": True,
                "domain": {"data": "temporal_weights", "field": "y1"}
            },
            {
                "name": "color",
                "type": "ordinal",
                "range": "category",
                "domain": {"data": "temporal_weights", "field": "topic"}
            },
            {
                "name": "font",
                "type": "sqrt",
                "range": [0, 20], "round": True, "zero": True,
                "domain": {"data": "series", "field": "argmax.value"}
            },
            {
                "name": "opacity",
                "type": "quantile",
                "range": [0, 0, 0, 0, 0, 0.1, 0.2, 0.4, 0.7, 1.0],
                "domain": {"data": "series", "field": "argmax.value"}
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
                        "data": "temporal_weights",
                        "groupby": ["topic"]
                    }
                },
                "marks": [
                    {
                        "type": "area",
                        "from": {"data": "facet"},
                        "encode": {
                            "update": {
                                "x": {"scale": "xscale", "field": "bucket"},
                                "y": {"scale": "yscale", "field": "y0"},
                                "y2": {"scale": "yscale", "field": "y1"},
                                "fill": {"scale": "color", "field": "topic"},
                                "fillOpacity": {"value": 1.0}
                            },
                            "hover": {
                                "fillOpacity": {"value": 0.5}
                            },
                        },                    
                    }

                ]
            }
        ]

    @property
    def background(self):
        return "black"
