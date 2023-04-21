import logging
from secrets import token_hex as random_token
from django.urls import reverse
from rest_framework.serializers import Field
from pyochre.server.ochre.models import MachineLearningModel


logger = logging.getLogger(__name__)


class AudioTranscriptionField(Field):
    
    def __init__(self, object_id, *argv, **argd):
        self.field_name = "tabular_{}".format(random_token(6))        
        self.style = {}
        self.style["detector_type"] = argd.pop("detector_type", "object")
        self.style["base_template"] = "audio.html"
        self.style["template_pack"] = "ochre/template_pack"
        self.style["interactive"] = True
        model = MachineLearningModel.objects.get(id=object_id)
        self.style["endpoint_url"] = reverse("api:machinelearningmodel-apply", args=(model.id,))
    
    def get_default_value(self):
        return None
