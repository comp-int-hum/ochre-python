import logging
from django.conf import settings
from pyochre.server.ochre.vega import OchreVisualization


logger = logging.getLogger(__name__)


class WordCloud(OchreVisualization):
    def __init__(self, words, prefix=None):
        self.values = words
        self.prefix = prefix
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
