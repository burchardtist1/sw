import pytest
from django.conf import settings
from faker import Faker
from rest_framework.test import APIClient

from characters.models import Collection
from characters.services import CollectionService, InMemoryStarWarsAPI

fake = Faker()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Allows access to database for all tests.
    https://pytest-django.readthedocs.io/en/latest/faq.html#how-can-i-give-database-access-to-all-my-tests-without-the-django-db-marker"""
    pass


@pytest.fixture(autouse=True)
def django_settings():
    settings.DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"


@pytest.fixture
def collection_fixture(monkey_patch_services):
    def fixture() -> Collection:
        return monkey_patch_services.export()

    return fixture


@pytest.fixture(autouse=True)
def monkey_patch_services(monkeypatch):
    service = CollectionService(repo=InMemoryStarWarsAPI())
    service._fetch_homeworld = lambda self: fake.name()
    monkeypatch.setattr("characters.services.CollectionService", lambda: service)
    return service


@pytest.fixture
def api_client():
    return APIClient()
