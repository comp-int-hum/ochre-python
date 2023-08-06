import re
import logging
from importlib.resources import files
from django.conf import settings
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import MachineLearningModel
import pyochre.server.ochre.fields as fields


logger = logging.getLogger(__name__)


class MachineLearningModelInteractiveSerializer(OchreSerializer):

    class Meta:
        model = MachineLearningModel
        fields = [
        ]

    def __init__(self, *argv, **argd):
        super(MachineLearningModelInteractiveSerializer, self).__init__(*argv, **argd)

    def to_representation(self, instance):
        miq_string = files("pyochre").joinpath(
            "data/model_interaction_query.sparql"            
        ).read_text()
        interactions = {}
        for binding in list(
                instance.query_signature(miq_string)
        ):
            name = re.sub("^{}".format(settings.OCHRE_NAMESPACE), "", str(binding["s"]))
            desc = binding["desc"].value
            param_name = binding["paramLabel"].value if binding.get("paramLabel") else None
            param_value = binding.get("paramValue")
            interactions[name] = interactions.get(
                name,
                {
                    "parameters" : {},
                    "description" : desc,                    
                    "field_class" : getattr(fields, binding.get("field_class").value)
                }
            )
            if param_name != None:
                interactions[name]["parameters"][param_name] = param_value
        retval = {}
        for i, (name, inter) in enumerate(interactions.items()):            
            fn = "field_{}".format(i)
            self._declared_fields[fn] = inter["field_class"](
                **inter.get("parameters", {}),
                label=inter["description"]
            )
            self.Meta.fields.append(fn)
            retval[fn] = self._declared_fields[fn].to_representation(instance)
        return retval

