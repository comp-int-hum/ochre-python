import logging
from django.conf import settings
from rest_framework.serializers import ModelSerializer, HiddenField, HyperlinkedIdentityField, CurrentUserDefault, CharField, HyperlinkedRelatedField, ListField, Serializer
from pyochre.server.ochre.fields import VegaField, ActionOrInterfaceField, AnnotatedObjectField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import Annotation, MachineLearningModel, Query, PrimarySource
from pyochre.server.ochre.vega import  TemporalEvolution, SpatialDistribution, WordCloud
from rdflib import Namespace
import requests


logger = logging.getLogger(__name__)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func


@shared_task
def annotation_from_machinelearningmodel(
        annotation_id,
        primarysource_id,
        machinelearningmodel_id,
        query_id=None
):
    ann = Annotation.objects.get(id=annotation_id)
    try:
        ps = PrimarySource.objects.get(id=primarysource_id)
        ml = MachineLearningModel.objects.get(id=machinelearningmodel_id)
        q = None if not query_id else Query.objects.get(id=query_id)
        data_graph = ps.data
        domain_graph = ps.domain
        #for x in domain_graph:
        #    print(x)
            
        #print(type(domain_graph)) #, len(domain_graph))
        response = requests.post(
            "{}/v2/models/{}/infer".format(
                settings.TORCHSERVE_INFERENCE_ADDRESS,
                ml.id
            ),
            data={
                "data_graph" : data_graph,
                "domain_graph" : domain_graph
            }
            #files={k : v[0] if isinstance(v, list) else v for k, v in argd.items()}
        )
        ann.state = ann.COMPLETE
        ann.save(annotation_graph=response.json()["output_graph"])
        ann.delete()
    except Exception as e:
        ann.delete()
        raise e


class AnnotationComputationalSerializer(OchreSerializer):
    machinelearningmodel = HyperlinkedRelatedField(
        queryset=MachineLearningModel.objects.all(),
        view_name="api:machinelearningmodel-detail",
        write_only=True,
        allow_null=False
    )
    query = HyperlinkedRelatedField(
        queryset=Query.objects.all(),
        view_name="api:query-detail",
        required=False,
        allow_null=True
    )
    primarysource = HyperlinkedRelatedField(
        queryset=PrimarySource.objects.all(),
        view_name="api:primarysource-detail",
    )
    class Meta:
        model = Annotation
        exclude = ["user"]

    def create(self, validated_data):
        obj = Annotation(
            name=validated_data["name"],
            machinelearningmodel=validated_data["machinelearningmodel"],
            primarysource=validated_data["primarysource"],
            created_by=validated_data["created_by"],
            state=PrimarySource.PROCESSING,            
            message="This annotation is in-progress..."
        )
        obj.save()
        annotation_from_machinelearningmodel.delay(
            obj.id,
            validated_data["primarysource"].id,
            validated_data["machinelearningmodel"].id,
            validated_data["query"].id if validated_data.get("query", False) else None,
        )
        return obj
