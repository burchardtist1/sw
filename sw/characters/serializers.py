from rest_framework import serializers

from characters.models import Collection


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ("id", "created_at")


class CountRequestSerializer(serializers.Serializer):
    collection_id = serializers.IntegerField()
    headers = serializers.ListSerializer(child=serializers.CharField())


class CountResponseSerializer(serializers.Serializer):
    pass
