import io
import re
from xml.etree import ElementTree as et
from pyochre.primary_sources import Processor


class XmlProcessor(Processor):

    def generate_events(self, fd):
        yield ("start", "document", {}, None)
        for event_type, element in et.iterparse(fd, events=["start", "end"]):
            yield (event_type, element.tag, element.attrib, element.text)
        yield ("end", "document", {}, None)
