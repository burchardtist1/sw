import pytest
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from rest_framework import status

from characters.models import Collection


def test_fetch(api_client):
    response = api_client.post(reverse("collections"))
    assert response.status_code == status.HTTP_201_CREATED
    qs = Collection.objects.all()
    assert qs.count() == 1

    collection = qs.first()
    data = response.data
    assert collection.id == data["id"]
    assert collection.created_at == parse_datetime(data["created_at"])


@pytest.mark.xfail
def test_count(api_client, collection_fixture):

    # invalid collection_id
    response = api_client.get(reverse("count") + "?collection_id=-1")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    collection = collection_fixture()
    response = api_client.get(
        reverse("count")
        + f"?collection_id={collection.id}&headers=homeworld&headers=birth_year"
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.data

@pytest.mark.xfail
def test_count_invalid_headers(api_client, collection_fixture):
    collection = collection_fixture()

    response = api_client.get(
        reverse("count")
        + f"?collection_id={collection.id}&headers=homeworld&headers=fail"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.xfail
def test_get_collection():
    pass
