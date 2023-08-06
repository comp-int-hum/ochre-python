import logging
from pyochre.server.ochre.serializers import DocumentationSerializer
from pyochre.server.ochre.models import Documentation
from pyochre.server.ochre.viewsets import OchreViewSet
from pyochre.server.ochre.autoschemas import OchreAutoSchema


logger = logging.getLogger(__name__)


class DocumentationViewSet(OchreViewSet):
    serializer_class = DocumentationSerializer
    model = Documentation
    queryset = Documentation.objects.all()
    schema = OchreAutoSchema(
        tags=["documentation"],
        component_name="documentation",
        operation_id_base="documentation"
    )

    def list(self, request, pk=None):
        """
        List documentation objects.
        """
        return self._list(request)

    def retrieve(self, request, pk=None):
        """
        Get information about a documentation object.
        """
        return self._retrieve(request, pk=pk)

    def destroy(self, request, pk=None):
        """
        Destroy (delete) a documentation object.
        """
        return self._destroy(request, pk)
    
