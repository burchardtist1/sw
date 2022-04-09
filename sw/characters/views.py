from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from characters.models import Collection
from characters.serializers import CollectionSerializer
from characters.services import CollectionService


class CollectionView(ListCreateAPIView):
    queryset = Collection.objects.all().order_by("created_at")
    serializer_class = CollectionSerializer

    def create(self, request, *args, **kwargs):
        service = CollectionService()
        collection = service.export()
        serializer = CollectionSerializer(collection)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
