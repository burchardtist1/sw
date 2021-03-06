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


def test_list_collections(api_client, collection_fixture):
    collection_1, collection_2 = collection_fixture(), collection_fixture()

    response = api_client.get(reverse("collections"))
    assert response.status_code == status.HTTP_200_OK

    data = response.data
    assert data["count"] == 2
    assert {collection_1.id, collection_2.id} == {x["id"] for x in data["results"]}


def test_count(api_client, collection_fixture):

    # invalid collection_id
    response = api_client.get(reverse("count", kwargs=dict(pk=-1)))
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    collection = collection_fixture()
    response = api_client.get(
        reverse("count", kwargs=dict(pk=collection.id))
        + f"?headers=homeworld&headers=mass"
    )
    assert response.status_code == status.HTTP_200_OK
    assert [all([x["homeworld"], x["mass"], x["count"] == 1]) for x in response.data]

    response = api_client.get(
        reverse("count", kwargs=dict(pk=collection.id))
        + f"?headers=height&headers=mass"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == [{"height": "90", "mass": "100", "count": 3}]


def test_count_invalid_headers(api_client, collection_fixture):
    collection = collection_fixture()

    response = api_client.get(
        reverse("count", kwargs=dict(pk=collection.id))
        + f"?headers=homeworld&headers=fail"
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
