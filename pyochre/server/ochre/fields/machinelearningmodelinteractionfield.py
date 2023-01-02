import logging
from pyochre.server.ochre.fields import MonacoEditorField, ObjectDetectionField
from pyochre.server.ochre.models import MachineLearningModel


logger = logging.getLogger(__name__)


class MachineLearningModelInteractionField(MonacoEditorField):

    def get_actual_field(self, parent_style, *argv, **argd):
        model = MachineLearningModel.objects.get(id=parent_style["object_id"])
        if True:
            return ObjectDetectionField(parent_style["object_id"], detector_type="object")
        #"text" if "ocr" in handler else "object")
        elif handler == "image_classifier":
            pass
        elif handler == "text_classifier":
            pass
        elif handler == "image_segmenter":
            pass
        elif handler == "text_generator":
            pass
        else:            
            return self
    
    def __init__(self, *argv, **argd):
        retval = super(MachineLearningModelInteractionField, self).__init__(*argv, **argd)
        self.style["hide_label"] = True
        self.style["interactive"] = True
