import logging
from django.conf import settings
from rest_framework.serializers import FileField, URLField, SerializerMethodField, HyperlinkedIdentityField, CharField, IntegerField, HyperlinkedRelatedField
from pyochre.server.ochre.serializers import OchreSerializer
from pyochre.server.ochre.fields import ActionOrInterfaceField
from pyochre.server.ochre.models import MachineLearningModel
from pyochre.server.ochre.fields import MachineLearningModelInteractionField
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
    # query_results = None if query == None else primarysource.query(query.sparql)
    #data_graph = rdflib.Graph()
    data_graph = primarysource.data.serialize(format="turtle")
    #None if query_results != None else primarysource.data
    domain_graph = primarysource.domain.serialize(format="turtle")
    #data_graph.add((OCHRE["rew"], OCHRE["hasPart"], OCHRE["dsaa"]))
    #data_graph.add((OCHRE["dsaa"], OCHRE["hasLabel"], Literal("aprill")))
    #data_graph.add((OCHRE["dsaa"], OCHRE["isA"], OCHRE["Token"]))
    response = requests.post(
        "{}/v2/models/{}/infer".format(
            settings.TORCHSERVE_INFERENCE_ADDRESS,
            model_id
        ),
        files={
            "data_graph" : StringIO(data_graph), #.serialize(format="turtle"),
            "domain_graph" : StringIO(domain_graph) #.serialize(format="turtle")
        }
        #files={
        #    k : v[0] if isinstance(v, list) else v for k, v in argd.items()
        #}
    )
    out = response.json()["output_graph"]
    annotation_graph = Graph()
    annotation_graph.parse(data=out, format="turtle")
    #print(len(out))
    # anns = model.apply(
    #     #singleton=None,
    #     #query_results=query_results,
    #     data_graph=data_graph,
    #     domain_graph=domain_graph
    # )
    annotation.state = annotation.COMPLETE
    #anns = json.loads(anns)
    #print(list(anns.keys()))
    annotation.save(annotation_graph=annotation_graph)

    

class MachineLearningModelSerializer(OchreSerializer):
    apply_url = MachineLearningModelInteractionField(
        view_name="api:machinelearningmodel-apply",
    )
    class Meta:
        model = MachineLearningModel
        fields = [
            "name",
            "apply_url",
            "url",
            "created_by",
            "creator",
            "id",
        ]
        
    # def create(self, validated_data):
    #     obj = MachineLearningModel(
    #         name=validated_data["name"],
    #         created_by=validated_data["created_by"],
    #     )
    #     return self.update(obj, validated_data)

    # def update(self, instance, validated_data):
    #     instance = super(
    #         MachineLearningModelSerializer,
    #         self
    #     ).update(
    #         instance,
    #         validated_data
    #     )
    #     if "huggingface_name" in validated_data:
    #         import_huggingface_model.delay(
    #             validated_data["name"],
    #             validated_data["created_by"].id,
    #             validated_data["huggingface_name"]
    #         )
    #     elif "mar_file" in validated_data:
    #         pass
    #     elif "topic_count" in validated_data:
    #         train_topic_model.delay(
    #             validated_data["name"],
    #             validated_data["created_by"].id,
    #             validated_data.get("query"),
    #             validated_data.get("primarysource"),
    #             lowercase=validated_data.get("lowercase", True),
    #             topic_count=validated_data.get("topic_count", 10),
    #             stopwords=validated_data.get("stopwords", [])
    #         )

    #         pass
    #     else:
    #         pass

    #     instance.save(**validated_data)
    #     return instance
