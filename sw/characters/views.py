from django.http import FileResponse
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from characters.models import Character, Collection
from characters.serializers import (
    CharacterSerializer,
    CollectionDetailsSerializer,
    CollectionSerializer,
    CountRequestSerializer,
)
from characters.services import CollectionService, StarWarsError


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
    def get(self, request, pk, format=None):
        params = request.query_params
        request_serializer = CountRequestSerializer(
            data=dict(
                headers=params.getlist("headers"),
            )
        )
        request_serializer.is_valid(True)

        service = CollectionService()
        data = request_serializer.data
        try:
            collection = service.get_collection(pk)
        except Collection.DoesNotExist as e:
            raise ValidationError from e

        try:
            response_data = service.aggregate(collection=collection, **data)
        except StarWarsError as e:
            raise ValidationError from e

        return Response(list(response_data), status=status.HTTP_200_OK)


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


class CharactersView(ListAPIView):
    serializer_class = CharacterSerializer

    def get_queryset(self):
        return Character.objects.filter(collection=self.kwargs["pk"])
