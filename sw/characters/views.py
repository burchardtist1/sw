from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from characters.models import Collection
from characters.serializers import (
    CollectionSerializer,
    CountRequestSerializer,
    CountResponseSerializer,
)
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


class CountView(APIView):
    def get(self, request, format=None):
        params = request.query_params
        request_serializer = CountRequestSerializer(
            data=dict(
                collection_id=params.get("collection_id"),
                headers=params.getlist("headers"),
            )
        )
        request_serializer.is_valid(True)

        service = CollectionService()
        data = request_serializer.data
        collection = service.get_collection(data.pop("collection_id"))

        response_data = service.aggregate(collection=collection, **data)
        response_serializer = CountResponseSerializer(data=response_data, many=True)
        response_serializer.is_valid(True)

        return Response(response_data, status=status.HTTP_200_OK)
