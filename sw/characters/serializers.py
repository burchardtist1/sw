from django.urls import reverse
from rest_framework import serializers

from characters.models import Collection


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ("id", "created_at")


class CollectionDetailsSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ("created_at", "file_name", "file_url")

    def get_file_name(self, obj):
        return obj.file.name.split("/")[-1]

    def get_file_url(self, obj):
        return reverse("download", kwargs=dict(pk=obj.id))


class CountRequestSerializer(serializers.Serializer):
    collection_id = serializers.IntegerField()
    headers = serializers.ListSerializer(child=serializers.CharField())


class CountResponseSerializer(serializers.Serializer):
    pass
