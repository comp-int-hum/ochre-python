import logging
from pyochre.server.ochre.vega import OchreVisualization
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import SH, RDF, RDFS
import rdflib
import json
from datetime import datetime
import os.path
from django.conf import settings


logger = logging.getLogger(__name__)


q = """
PREFIX ochre: <%s://%s/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?s ?np ?sn ?rc ?pn ?cn ?dt
WHERE
{
    ?s rdf:type sh:NodeShape .
    ?s sh:name ?sn .
    ?s sh:property ?p .
    ?p sh:name ?pn .
    ?p sh:path ?np .
    optional {
      ?p sh:class|(sh:or/sh:class) ?rc .
      ?rc sh:name ?cn .
    }
    optional {
      ?p sh:datatype ?dt .
    }
}
""" % (settings.PROTO, settings.HOSTNAME)


class PrimarySourceDomainGraph(OchreVisualization):

    def __init__(self, domain, prefix=None):
        self.prefix = prefix
        g = Graph()
        for tr in domain:
            g.add(tr)
        entities, relationships, properties = {}, [], []
        for s, np, sn, rc, pn, cn, dt in g.query(q):
            entities[sn] = entities.get(
                sn,
                {
                    "entity_name" : str(sn),
                    "entity_url" : str(s),
                    "properties" : [{}]
                }
            )
            if cn:
                entities[cn] = entities.get(
                    cn,
                    {
                        "entity_name" : str(cn),
                        "entity_url" : str(rc),
                        "properties" : [{}]
                    }
                )
                relationships.append(
                    {
                        "source" : str(sn),
                        "target" : str(cn),
                        "source_name" : str(sn),
                        "relationship_name" : str(pn),
                        "relationship_url" : str(rc),
                        "target_name" : str(cn)
                    }
                )
            else:
                entities[sn]["properties"].append(
                    {
                        "property_name" : str(pn),
                        "property_type" : str(dt).split("#")[-1],
                        "property_url" : str(dt)
                    }
                )
        self._entities = list(entities.values())
        self._relationships = relationships
        super(PrimarySourceDomainGraph, self).__init__()

    @property
    def signals(self):
        return [
            {"name": "width", "value": 800},
            {"name": "height", "value": 350},
            { "name": "cx", "update": "width / 2" },
            { "name": "cy", "update": "height / 2" },
            { "name": "nodeRadius", "update": "zoom * 20"},
            { "name": "nodeCharge", "value": -30},
            { "name": "linkDistance", "update": "zoom * 200"},
            { "name": "static", "value": True},
            {
                "description": "State variable for active node fix status.",
                "name": "fix", "value": False,
                "on": [
                    {
                        "events": "*:mouseout[!event.buttons], window:mouseup",
                        "update": "false"
                    },
                    {
                        "events": "*:mouseover",
                        "update": "fix || true"
                    },
                    {
                        "events": "[symbol:mousedown, window:mouseup] > window:mousemove!",
                        "update": "xy()",
                        "force": True
                    }
                ]
            },
            {
                "description": "Graph node most recently interacted with.",
                "name": "node", "value": None,
                "on": [
                    {
                        "events": "symbol:mouseover",
                        "update": "fix === true ? group() : node"
                    }
                ]
            },
            {
                "description": "Flag to restart Force simulation upon data changes.",
                "name": "restart", "value": False,
                "on": [
                    {"events": {"signal": "fix"}, "update": "fix && fix.length"}
                ]
            },
            {
                "name": "zoom",
                "value": 0.75,
                "on": [{
                    "events": {"type": "wheel", "consume": True},
                    "update": "clamp(zoom * pow(1.0005, -event.deltaY * pow(16, event.deltaMode)), 0.1, 1)"
                }]
            },
        ]

    @property
    def data(self):
        return [
            {
                "name": "entities",
                "values" : self._entities,
            },
            {
                "name": "relationships",
                "values" : self._relationships,
            },
        ]
    
    @property
    def scales(self):
        return [
        ]
    
    @property
    def axes(self):
        return []

    @property
    def marks(self):
        return [
            {
                "type" : "group",
                "name" : "node_group",
                "zindex": 1,
                "on" : [
                    {
                        "trigger": "fix",
                        "modify": "node",
                        "values": "fix === true ? {fx: node.x, fy: node.y} : {fx: fix[0], fy: fix[1]}"
                    },
                    {
                        "trigger": "!fix",
                        "modify": "node", "values": "{fx: null, fy: null}"
                    }
                ],
                "scales": [
                    {
                        "name": "property_scale",
                        "type": "band",
                        "domain": {"data": "entity", "field": "property_name"},
                        "range": {"step": {"signal" : "zoom * 10"}}
                    }
                ],
                "encode": {
                    "enter": {
                        "stroke": {"value": "blue"}
                    },
                    "update": {
                        "size": {"signal": "25 * nodeRadius * nodeRadius"},
                    }
                },
                "from" : {
                    "facet" : {
                        "data" : "entities",
                        "field" : "properties",
                        "name" : "entity"
                    }
                },
                "scales": [
                    {
                        "name": "property_scale",
                        "type": "band",
                        "domain": {
                            "data": "entity",
                            "field": "property_name"
                        },
                        "range": {
                            "step": {
                                "signal": "zoom * 10"
                            }
                        }
                    }
                ],
                "marks" : [
                    {
                        "type" : "symbol",
                        "from" : {"data" : "entity"},
                        "name" : "entityBackground",
                        "encode": {
                            "enter": {
                                "fill": {"value" : "lightblue"},
                                "stroke": {"value": "blue"}
                            },
                            "update": {
                                "shape" : {"value" : "M-1.5,-1H1.5V0.5H-1.5Z"},
                                "size": {"signal": "30 * nodeRadius * nodeRadius"},
                                "cursor": {"value": "pointer"},
                                "zindex" : {"value" : 1},

                            }
                        }
                    },
                    {
                        "type" : "text",
                        "from" : {"data" : "entityBackground"},
                        "encode" : {
                            "enter": {
                                "fill": {"value" : "red"},
                                "y":{
                                    "offset": {"signal" : "-zoom * 35"}
                                },
                            },
                            "update": {
                                "align" : {"value" : "center"},
                                "fontSize" : {"signal" : "zoom * 15"},
                                "fontStyle" : {"value" : "bold"},
                                "fill": {"value" : "red"},
                                "text" : {"signal" : "parent.entity_name"},
                                "y":{
                                    "offset": {"signal" : "-zoom * 35"}
                                }
                            }                            
                        }
                    },
                    {
                        "type": "text",
                        "zindex": 3,
                        "from": {"data": "entity"},
                        "encode": {
                            "enter": {
                                "fill": {"value": "black"},
                                "y": {
                                    "scale": "property_scale",
                                    "field": "property_name",
                                }
                            },
                            "update": {
                                "align": {"value": "center"},
                                "fontSize": {"signal": "zoom * 10"},
                                "fontStyle": {"value": "bold"},
                                "fill": {"value": "black"},
                                "text": {"field": "property_name"},
                                "y": {
                                    "scale": "property_scale",
                                    "field": "property_name",
                                    "offset": {"signal" : "-zoom * 20"}
                                }

                            },
                            
                        }
                    }                    
                ],                
                "transform": [
                    {
                        "type": "force",
                        "iterations": 300,
                        "restart": {"signal": "restart"},
                        "static": {"signal": "static"},
                        "signal": "force",
                        "forces": [
                            {"force": "center", "x": {"signal": "cx"}, "y": {"signal": "cy"}},
                            {"force": "collide", "radius": {"signal": "nodeRadius * 2"}},
                            {"force": "nbody", "strength": {"signal": "nodeCharge / 10"}},
                            {"force": "link", "links": "relationships", "distance": {"signal": "linkDistance"}, "id" : "datum.entity_name"}
                        ]
                    }
                ]
            },
            {
                "type": "path",
                "name" : "links",
                "from": {"data": "relationships"},
                "encode": {
                    "update": {
                        "stroke": {"value": "#aaa"},
                        "strokeWidth": {"signal": "zoom * 10"},
                        "tooltip" : {"field" : "relationship_name"},
                        "href" : {"field" : "relationship_url"}
                    }
                },
                "transform": [
                    {
                       "type": "linkpath",
                       "require": {"signal": "force"},
                       "shape": "line",
                       "sourceX": "datum.source.x",
                       "sourceY": "datum.source.y",
                       "targetX": "datum.target.x",
                       "targetY": "datum.target.y"
                    },
                ]
            },
        ]


