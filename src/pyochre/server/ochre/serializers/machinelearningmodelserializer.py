import logging
from django.conf import settings
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField, IntegerField, HyperlinkedRelatedField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import MachineLearningModel
import requests
from rdflib import Namespace


logger = logging.getLogger(__name__)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


@shared_task
def apply_machinelearningmodel(annotation_id, model_id, primarysource_id, query_id=None):
    model = MachineLearningModel.objects.get(id=model_id)
    primarysource = PrimarySource.objects.get(id=primarysource_id)
    query = None if query_id == None else Query.objects.get(id=query_id)
    annotation = Annotation.objects.get(id=annotation_id)
    annotation.message="Annotating data"
    annotation.state = annotation.PROCESSING
    annotation.save()
    data_graph = primarysource.data.serialize(format="turtle")
    domain_graph = primarysource.domain.serialize(format="turtle")
    response = requests.post(
        "{}/v2/models/{}/infer".format(
            settings.TORCHSERVE_INFERENCE_ADDRESS,
            model_id
        ),
        files={
            "data_graph" : StringIO(data_graph),
            "domain_graph" : StringIO(domain_graph)
        }
    )
    out = response.json()["output_graph"]
    annotation_graph = Graph()
    annotation_graph.parse(data=out, format="turtle")
    annotation.state = annotation.COMPLETE
    annotation.save(annotation_graph=annotation_graph)
    

class MachineLearningModelSerializer(OchreSerializer):
    url = HyperlinkedIdentityField(
        view_name="api:machinelearningmodel-detail",
        lookup_field="id",
        lookup_url_kwarg="pk"
    )
    apply_url = HyperlinkedIdentityField(
        view_name="api:machinelearningmodel-apply",
        lookup_field="id",
        lookup_url_kwarg="pk"
    )
    signature_url = HyperlinkedIdentityField(
        view_name="api:machinelearningmodel-signature",
        lookup_field="id",
        lookup_url_kwarg="pk"
    )
    properties_url = HyperlinkedIdentityField(
        view_name="api:machinelearningmodel-properties",
        lookup_field="id",
        lookup_url_kwarg="pk"
    )
    permissions_url = HyperlinkedIdentityField(
        view_name="api:machinelearningmodel-permissions",
        lookup_field="id",
        lookup_url_kwarg="pk"
    )    
    class Meta:
        model = MachineLearningModel
        fields = [
            "name",
            "id",
            "url",
            "apply_url",
            "properties_url",
            "signature_url",
            "permissions_url",
            #"created_by",
            "creator_url"
        ]

    def creation_methods(self):
        return [
            {
                "title" : "Create from XSL transformation",
                "url" : "api:primarysource-create_from_xsl_transformation"
            },
            {
                "title" : "Create from HathiTrust collection",
                "url" : "api:primarysource-create_from_hathitrust_collection"
            }
        ]
        
