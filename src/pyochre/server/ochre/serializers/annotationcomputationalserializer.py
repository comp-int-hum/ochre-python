import logging
from django.conf import settings
from rest_framework.serializers import ModelSerializer, HiddenField, HyperlinkedIdentityField, CurrentUserDefault, CharField, HyperlinkedRelatedField, ListField, Serializer, BooleanField
from pyochre.server.ochre.fields import VegaField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.models import Annotation, MachineLearningModel, Query, PrimarySource
from pyochre.server.ochre.vega import  TemporalEvolution, SpatialDistribution, WordCloud
from pyochre.utils import ochrequery as OQ
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
        initial_query = None if not query_id else Query.objects.get(id=query_id)
        for binding in ml.signature.query(
                OQ(
                    """
                    SELECT ?q WHERE
                    {
                    ?qid ochre:instanceOf ochre:Query .
                    ?qid ochre:hasValue ?q .
                    }
                    """
                )
        ):
            model_query = OQ(binding["q"].value)
            
        if initial_query:
            data_graph = ps.query(OQ(initial_query.sparql))
        else:
            data_graph = ps.data

        res = data_graph.query(model_query)
        response = requests.post(
            "{}/v2/models/{}/infer".format(
                settings.TORCHSERVE_INFERENCE_ADDRESS,
                ml.id
            ),
            data={
                "data" : res.serialize(format="xml"),
                #"domain_graph" : domain_graph.serialize(format="turtle")
            }
        )
        ann.state = ann.COMPLETE
        ann.message = ""
        ann.save(annotation_graph=response.json()["output_graph"])
    except Exception as e:
        ann.delete()
        raise e


class AnnotationComputationalSerializer(OchreSerializer):
    name = CharField(
        max_length=2000,
        required=False,
        label="Name",
        help_text="Names must be unique for the user and type of object.",
    )
    machinelearningmodel = HyperlinkedRelatedField(
        queryset=MachineLearningModel.objects.all(),
        view_name="api:machinelearningmodel-detail",
        write_only=True,
        allow_null=False,
        help_text="The machine learning model to apply."
    )
    primarysource = HyperlinkedRelatedField(
        queryset=PrimarySource.objects.all(),
        view_name="api:primarysource-detail",
        help_text="The primary source to annotate."
    )
    query = HyperlinkedRelatedField(
        queryset=Query.objects.all(),
        view_name="api:query-detail",
        required=False,
        allow_null=True,
        help_text="Optional query to filter or transform the primary source."
    )
    force = BooleanField(
        required=False,
        write_only=True,
        allow_null=True,
        default=False,
        help_text="Overwrite any existing annotation of the same name and creator."
    )

    class Meta:
        model = Annotation
        exclude = ["user"]

    def create(self, validated_data):
        if validated_data.get("force", False):
            for existing in Annotation.objects.filter(
                    name=validated_data["name"],
                    created_by=validated_data["created_by"]
            ):
                existing.delete()
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
