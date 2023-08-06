import os.path
from django.template.loaders.base import Loader
from django.template.base import Origin
from django.template import TemplateDoesNotExist

class OchreLoader(Loader):
    def __init__(self, *argv, **argd):
        self.file_names = {k : v for k, v in argv[-1].items() if v}
        super(OchreLoader, self).__init__(*argv[:-1], **argd)

    def get_template_sources(self, template_name):
        if template_name in self.file_names:
            yield Origin(
                self.file_names[template_name],
                template_name,
                self
            )
        else:
            return

    def get_contents(self, origin):
        if not os.path.exists(origin.name):
            raise TemplateDoesNotExist("No such file: '{}'".format(origin.name))
        with open(origin.name, "rt") as ifd:
            return ifd.read()
