import logging
from pyochre.server.ochre.vega import OchreVisualization
from rdflib import Graph, URIRef, Literal, BNode
from importlib.resources import files
from rdflib.namespace import SH, RDF, RDFS
import rdflib
import re
import json
from datetime import datetime
import os.path
from django.conf import settings


logger = logging.getLogger(__name__)


rx = re.compile("^{}(.*)$".format(settings.OCHRE_NAMESPACE))


class PrimarySourceDomainGraph(OchreVisualization):

    def __init__(self, object, prefix=None):
        self.prefix = prefix
        query = files("pyochre").joinpath(
            "data/domain_graph_visualization_query.sparql"
        ).read_text()
        entities, relationships, properties = {}, [], []
        for s, np, sn, rc, pn, cn, dt in object.domain.query(query):
            sn = rx.sub(r"\1", str(sn))            
            pn = rx.sub(r"\1", str(pn))
            s = str(s)
            rc = str(rc)
            entities[sn] = entities.get(
                sn,
                {
                    "entity_name" : sn,
                    "entity_url" : s,
                    "properties" : [{}]
                }
            )
            if cn:
                cn = rx.sub(r"\1", str(cn))
                entities[cn] = entities.get(
                    cn,
                    {
                        "entity_name" : cn,
                        "entity_url" : rc,
                        "properties" : [{}]
                    }
                )
                relationships.append(
                    {
                        "source" : sn,
                        "target" : cn,
                        "source_name" : sn,
                        "relationship_name" : pn,
                        "relationship_url" : rc,
                        "target_name" : cn
                    }
                )
            else:
                entities[sn]["properties"].append(
                    {
                        "property_name" : pn,
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
                                "size": {"signal": "40 * nodeRadius * nodeRadius"},
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


