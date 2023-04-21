import logging
import io
import re
from xml.etree import ElementTree as et
from lxml.etree import XMLTreeBuilder, TreeBuilder


logger = logging.getLogger(__name__)


class XmlParser(TreeBuilder):
    pass
