import io
import re
import json
import argparse
import gzip
import xml.sax
import sys
from xml.etree import ElementTree as et
from dataclasses import dataclass, field
from typing import Any
from pyochre.primary_sources import Processor


@dataclass
class TEIHandler(xml.sax.handler.ContentHandler):
    structural_elements: Any
    content_elements: Any
    content_passthrough_elements: Any
    relationship_elements: Any 
    relationships: Any
    content_property: Any = "content"
    id_property: Any = "id"
    entity_type_property: Any = "entity_type"
    name: Any = ""
    owners: Any = field(default_factory=list)
    description: Any = ""
    domain: Any = ""
    relationships: Any = field(default_factory=dict)
    unique_ids: Any = field(default_factory=set)
    properties: Any = field(default_factory=set)
    not_numeric: Any = field(default_factory=set)
    entity_types: Any = field(default_factory=dict)
    unique_values: Any = field(default_factory=dict)
    categorical_limit: Any = 50
    ids_to_types: Any = field(default_factory=dict)
    all_entities: Any = field(default_factory=dict)
    location = []
    target: Any = None
    
    #def __init__(self, target):
    #    super(TEIHandler, self).__init__()
    #    self.target = target        
    
    def startDocument(self):
        self.location = []
        self.auto_ids = 0

    def startElement(self, name, attrs):
        if name in self.structural_elements + self.content_elements:
            self.entity_types[name] = self.entity_types.get(name, set())
            attr_names = attrs.getNames()
            if "id" in attr_names:
                eid = attrs.getValue("id")
            else:
                eid = "auto {}".format(self.auto_ids)
                self.auto_ids += 1
            entity = {
                "__content_entity__" : name in self.content_elements,
                "__content__" : [],
                self.id_property : eid,
                self.entity_type_property : name,
            }
            self.ids_to_types[eid] = name
            if name in self.content_elements:
                qn = "{}_{}".format(name, self.content_property)
                self.entity_types[name].add(qn)
            for n in [x for x in attr_names if x != "id"]:
                val = attrs.getValue(n)
                if n in self.relationships:
                    rel_type = "{}_{}".format(name, n)
                    self.relationships[rel_type] = self.relationships.get(rel_type, [])
                    for v in val.split():                        
                        self.relationships[rel_type].append({"source" : eid, "target" : v})
                else:                    
                    qn = "{}_{}".format(name, n)
                    self.unique_values[qn] = self.unique_values.get(qn, set())
                    self.unique_values[qn].add(val)
                    self.entity_types[name].add(qn)
                    #if qn == "place_itcity":
                    #    print(self.entity_types["place"])
                    self.properties.add(qn)
                    if val == None or re.match("^\s+$", val):
                        continue
                    try:
                        val = float(val)
                    except:
                        self.not_numeric.add(qn)
                    entity[qn] = val
            if eid in self.unique_ids:
                raise Exception("ID '{}' is already used".format(eid))
            self.unique_ids.add(eid)
            self.location.append(entity)
        elif name in self.relationship_elements:
            names = attrs.getNames()
            if "type" in names:
                assert(len([n for n in names if n not in ["type"]]) == 1)
                target_id = attrs.getValue([n for n in names if n not in ["type"]][0])
                rel_type = attrs.getValue("type")
                self.relationships[rel_type] = self.relationships.get(rel_type, [])
                for v in target_id.split():
                    self.relationships[rel_type].append({"source" : self.location[-1][self.id_property], "target" : v})

    def endElement(self, name):
        if name in self.structural_elements + self.content_elements:
            entity = self.location[-1]
            if name in self.content_elements:
                cf = "{}_{}".format(name, self.content_property)

                val = re.sub(r"\s+", " ", " ".join(entity["__content__"]))
                self.properties.add(cf)
                try:
                    val = float(val)
                except:
                    self.not_numeric.add(cf)
                self.unique_values[cf] = self.unique_values.get(cf, set())
                self.unique_values[cf].add(val)
                entity[cf] = val
            entity[self.entity_type_property] = name
            self.location = self.location[:-1]
            self.ids_to_types[entity[self.id_property]] = entity[self.entity_type_property]
            if "__content_entity__" in entity:
                del entity["__content_entity__"]
            if "__content__" in entity:
                del entity["__content__"]
            self.all_entities[entity[self.id_property]] = entity
            #self.ofd.write(json.dumps(entity) + "\n")

        elif name in self.relationship_elements:
            pass

    def characters(self, chars):
        if re.match(r"^\s*$", chars):
            return
        i = None
        for i in reversed(range(len(self.location))):
            if self.location[i]["__content_entity__"] == True:
                self.location[i]["__content__"].append(chars)
                break
        #if i == None:
        #    print(self.location)
        #    print(chars)

    def endDocument(self):
        #print(self.entity_types["place"])
        assert len(self.location) == 0
        self.meta = {
            "name" : self.name,
            "description" : self.description,
            "domain" : self.domain,
            "owners" : [],
            "id_property" : self.id_property,
            "entity_type_property" : self.entity_type_property,
        }
        self.properties = {
            name : {
                "type" : "scalar" if name not in self.not_numeric else "categorical" if len(self.unique_values.get(name)) < self.categorical_limit and max([len(str(x)) for x in self.unique_values.get(name, [])]) < 50 else "text"
            } for name in list(self.properties)
        }
        #self.relationships = {}
        for rel_type, rels in self.relationships.items():
            sources = set()
            targets = set()
            for rel in rels:
                sources.add(self.ids_to_types[rel["source"]])
                targets.add(self.ids_to_types[rel["target"]])
                self.all_entities[rel["source"]][rel_type] = self.all_entities[rel["source"]].get(rel_type, [])
                self.all_entities[rel["source"]][rel_type].append(rel["target"])
            assert len(sources) == 1 and len(targets) == 1
            self.relationships[rel_type] = {
                "source_entity_type" : sources.pop(),
                "target_entity_type" : targets.pop()
            }
        self.entity_types = {k : {"properties" : list(v)} for k, v in self.entity_types.items()}

    @property
    def data(self):
        return self.all_entities.values()

    @property
    def schema(self):
        print(self.entity_types["place"])
        return {
            "@context" : {
                "@vocab" : "http://schema.org"
            },
            "meta" : self.meta,
            "properties" : self.properties,
            "relationships" : self.relationships,
            "entity_types" : self.entity_types,
        }
# who ruler




class TeiProcessor(Processor):
    location = []
    auto_ids = 0
    
    def __call__(self, fd):
        for event_type, element in et.iterparse(fd, events=["start", "end"]):
            name = element.tag
            if event_type == "start":
                if name in self.schema["structural_elements"] + self.schema["content_elements"]:
                    pass
                    # self.entity_types[name] = self.entity_types.get(name, set())
                    # attr_names = attrs.getNames()
                    # if "id" in attr_names:
                    #     eid = attrs.getValue("id")
                    # else:
                    #     eid = "auto {}".format(self.auto_ids)
                    #     self.auto_ids += 1
                    # entity = {
                    #     "__content_entity__" : name in self.content_elements,
                    #     "__content__" : [],
                    #     self.id_property : eid,
                    #     self.entity_type_property : name,
                    # }
                    # self.ids_to_types[eid] = name
                    # if name in self.content_elements:
                    #     qn = "{}_{}".format(name, self.content_property)
                    #     self.entity_types[name].add(qn)
                    # for n in [x for x in attr_names if x != "id"]:
                    #     val = attrs.getValue(n)
                    #     if n in self.relationships:
                    #         rel_type = "{}_{}".format(name, n)
                    #         self.relationships[rel_type] = self.relationships.get(rel_type, [])
                    #         for v in val.split():                        
                    #             self.relationships[rel_type].append({"source" : eid, "target" : v})
                    #     else:                    
                    #         qn = "{}_{}".format(name, n)
                    #         self.unique_values[qn] = self.unique_values.get(qn, set())
                    #         self.unique_values[qn].add(val)
                    #         self.entity_types[name].add(qn)
                    #         #if qn == "place_itcity":
                    #         #    print(self.entity_types["place"])
                    #         self.properties.add(qn)
                    #         if val == None or re.match("^\s+$", val):
                    #             continue
                    #         try:
                    #             val = float(val)
                    #         except:
                    #             self.not_numeric.add(qn)
                    #         entity[qn] = val
                    # if eid in self.unique_ids:
                    #     raise Exception("ID '{}' is already used".format(eid))
                    # self.unique_ids.add(eid)
                    self.location.append(name)
                elif name in self.schema["relationship_elements"]:
                    names = attrs.getNames()
                    if "type" in names:
                        assert(len([n for n in names if n not in ["type"]]) == 1)
                        target_id = attrs.getValue([n for n in names if n not in ["type"]][0])
                        rel_type = attrs.getValue("type")
                        self.relationships[rel_type] = self.relationships.get(rel_type, [])
                        for v in target_id.split():
                            self.relationships[rel_type].append({"source" : self.location[-1][self.id_property], "target" : v})
                # ******
            elif event_type == "end":
                if name in self.schema["structural_elements"] + self.schema["content_elements"]:
                    #entity = self.location[-1]
                    #if name in self.schema["content_elements"]:
                        #cf = "{}_{}".format(name, self.content_property)
                        # val = re.sub(r"\s+", " ", " ".join(entity["__content__"]))
                        # self.properties.add(cf)
                        # try:
                        #     val = float(val)
                        # except:
                        #     self.not_numeric.add(cf)
                        # self.unique_values[cf] = self.unique_values.get(cf, set())
                        # self.unique_values[cf].add(val)
                        # entity[cf] = val
                    #    pass
                    #entity[self.entity_type_property] = name
                    self.location = self.location[:-1]
                    #self.ids_to_types[entity[self.id_property]] = entity[self.entity_type_property]
                    #if "__content_entity__" in entity:
                    #    del entity["__content_entity__"]
                    #if "__content__" in entity:
                    #    del entity["__content__"]
                    #self.all_entities[entity[self.id_property]] = entity
                    #self.ofd.write(json.dumps(entity) + "\n")

                elif name in self.schema["relationship_elements"]:
                    pass


                #print(element.tag, element.text)
                #self.send_triple("domain", element.tag, 2, 3)
    


# def tei_method(text, schema):
#     handler = TEIHandler(
#         schema["structural_elements"],
#         schema["content_elements"],
#         schema["content_passthrough_elements"],
#         schema["relationship_elements"],
#         schema["relationships"],
#         name="Hebrew Bible",
#         description="Leningrad Codex",
#         domain="Literature",
#         target=printer
#     )
#     #xml.sax.parseString(text, handler)
#     #for triple in xml.sax.parseString(text, handler):
#     fd = io.BytesIO(text)
#     #fd.write(b"<xml></xml>")
#     #print(fd.getvalue())
#     for triple in et.iterparse(fd):
#         yield triple

