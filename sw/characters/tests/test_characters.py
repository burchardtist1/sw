from django.urls import reverse
from django.utils.dateparse import parse_datetime
from rest_framework import status

from characters.models import Character, Collection


def test_fetch(api_client):
    response = api_client.post(reverse("collections"))
    assert response.status_code == status.HTTP_201_CREATED
    qs = Collection.objects.all()
    assert qs.count() == 1

    collection = qs.first()
    data = response.data
    assert collection.id == data["id"]
    assert collection.created_at == parse_datetime(data["created_at"])


def test_count(api_client, collection_fixture):

    # invalid collection_id
    response = api_client.get(reverse("count") + "?collection_id=-1")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    collection = collection_fixture()
    response = api_client.get(
        reverse("count")
        + f"?collection_id={collection.id}&headers=homeworld&headers=mass"
    )
    assert response.status_code == status.HTTP_200_OK
    assert [all([x["homeworld"], x["mass"], x["value"] == 1]) for x in response.data]

    response = api_client.get(
        reverse("count") + f"?collection_id={collection.id}&headers=height&headers=mass"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == [{"height": "90", "mass": "100", "value": 3}]


def test_count_invalid_headers(api_client, collection_fixture):
    collection = collection_fixture()

    response = api_client.get(
        reverse("count")
        + f"?collection_id={collection.id}&headers=homeworld&headers=fail"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_collection(api_client, collection_fixture):
    collection = collection_fixture()
    response = api_client.get(
        reverse("collection-details", kwargs=dict(pk=collection.id))
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.data
    assert data["file_name"]
    download_url = reverse("download", kwargs=dict(pk=collection.id))
    assert download_url == data["file_url"]


def test_list_characters(api_client, collection_fixture):
    collection = collection_fixture()
    response = api_client.get(reverse("characters", kwargs=dict(pk=collection.id)))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == Character.objects.count()
