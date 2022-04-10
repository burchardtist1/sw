from django.http import FileResponse
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from characters.models import Collection
from characters.serializers import (
    CollectionDetailsSerializer,
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


class CollectionDetailsView(APIView):
    def get(self, request, pk, format=None):
        service = CollectionService()
        collection = service.get_collection(pk)
        serializer = CollectionDetailsSerializer(collection)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        try:
            collection = service.get_collection(data.pop("collection_id"))
        except Collection.DoesNotExist as e:
            raise ValidationError from e

        response_data = service.aggregate(collection=collection, **data)
        response_serializer = CountResponseSerializer(data=response_data, many=True)
        response_serializer.is_valid(True)

        return Response(response_data, status=status.HTTP_200_OK)


class DownloadCSVView(APIView):
    def get(self, request, pk, format=None):
        service = CollectionService()
        collection = service.get_collection(pk)

        file_handle = collection.file.open()
        response = FileResponse(file_handle, content_type="text/csv")
        response["Content-Length"] = collection.file.size
        response["Content-Disposition"] = (
            'attachment; filename="%s"' % collection.file.name
        )

        return response
