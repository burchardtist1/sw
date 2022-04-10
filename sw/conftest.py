import petl as etl
import pytest
from django.conf import settings
from faker import Faker
from petl.io.sources import MemorySource
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
    settings.DEFAULT_FILE_STORAGE = "petl.io.sources.MemorySource"


@pytest.fixture
def collection_fixture(collection_service):
    def fixture() -> Collection:
        return collection_service.export()

    return fixture


@pytest.fixture(autouse=True)
def memory_source(monkeypatch):
    memory_source = MemorySource()
    setattr(memory_source, "path", lambda _: memory_source)
    monkeypatch.setattr("petl.io.sources.MemorySource", lambda: memory_source)


@pytest.fixture(autouse=True)
def collection_service(monkeypatch):
    service = CollectionService(repo=InMemoryStarWarsAPI())
    service.character_etl._fetch_homeworld = lambda self: fake.name()
    service.character_etl.load_table = lambda file: etl.fromcsv(
        MemorySource(file.storage.getvalue())
    )
    monkeypatch.setattr("characters.services.CollectionService", lambda: service)
    return service


@pytest.fixture
def api_client():
    return APIClient()
