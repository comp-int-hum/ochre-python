import json
from lxml.etree import TreeBuilder


def clean(s):
    return re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '', s)


class JsonParser(TreeBuilder):
    
    def __init__(self, *argv, **argd):
        super(JsonParser, self).__init__()

    def handle_value(self, value):
        if isinstance(value, list):
            self.start("list", {})
            for item in value:
                self.start("item", {})
                self.handle_value(item)
                self.end("item")
            self.end("list")
        elif isinstance(value, dict):
            self.start("object", {})
            for k, v in value.items():
                self.start("property", {"name" : k})
                self.handle_value(v)
                self.end("property")
            self.end("object")
        else:
            self.data(str(value))
    
    def __call__(self, fd, split=False):
        j = json.loads(fd.read())
        if split:            
            for sub in j.items() if isinstance(j, dict) else j:
                self.start("document", {})
                self.handle_value(
                    {sub[0] : sub[1]} if isinstance(j, dict) else [sub]
                )
                self.end("document")
                yield self.close()
        else:
            self.start("document", {})
            self.handle_value(j)
            self.end("document")
            yield self.close()


class JsonLineParser(TreeBuilder):
    
    def __init__(self, *argv, **argd):
        super(JsonLineParser, self).__init__()

    def handle_value(self, value):
        if isinstance(value, list):
            self.start("list", {})
            for item in value:
                self.start("item", {})
                self.handle_value(item)
                self.end("item")
            self.end("list")
        elif isinstance(value, dict):
            self.start("object", {})
            for k, v in value.items():
                self.start("property", {"name" : k})
                self.handle_value(v)
                self.end("property")
            self.end("object")
        else:
            self.data(str(value))
    
    def __call__(self, fd):
        self.start("document", {})
        for line in fd:
            self.start("item", {})
            self.handle_value(json.loads(line))
            self.end("item")
        self.end("document")
        return self.close()
    
