import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

import petl as etl
import requests
from dateutil import parser
from django.db import transaction
from django.db.models.fields.files import FieldFile
from faker import Faker
from rest_framework.serializers import ValidationError

from characters.models import Character, Collection

# https://stackoverflow.com/questions/24344045/how-can-i-completely-remove-any-logging-from-requests-module-in-python
logging.getLogger("urllib3").propagate = False

logger = logging.getLogger(__name__)

CharactersListTyping = list[dict[str, Any]]


class StarWarsError(ValidationError):
    pass


class StarWarsAPI:
    url: str = "https://swapi.dev/api/{endpoint}"

    @property
    def url_people(self) -> str:
        return self.url.format(endpoint="people")

    def get_people(self) -> CharactersListTyping:
        def get(url: str) -> dict[str, Any]:
            logger.debug(f"fetching {url}")
            response = requests.get(url)
            if not response.ok:
                raise StarWarsError(response.text)

            return response.json()

        result = list()
        next_page = self.url_people

        while next_page:
            response_data = get(next_page)
            result += response_data["results"]
            next_page = response_data["next"]

        return result


class InMemoryStarWarsAPI(StarWarsAPI):
    fake = Faker()

    def get_people(self) -> CharactersListTyping:
        return [
            {
                "name": self.fake.name(),
                "height": "90",
                "mass": "100",
                "hair_color": self.fake.name(),
                "skin_color": self.fake.name(),
                "eye_color": self.fake.name(),
                "birth_year": self.fake.name(),
                "gender": self.fake.name(),
                "homeworld": self.fake.name(),
                "edited": "2014-12-20T21:17:56.891000Z",
            }
            for _ in range(3)
        ]


class CharacterETL:
    header = [
        "name",
        "height",
        "mass",
        "hair_color",
        "skin_color",
        "eye_color",
        "birth_year",
        "gender",
        "homeworld",
        "edited",
    ]

    def transform(self, data: CharactersListTyping) -> etl.Table:
        table = etl.fromdicts(data, header=self.header)

        table = etl.rename(table, "edited", "date")

        homeworld_urls = etl.facet(table, "homeworld")
        homeworlds = {x: self._fetch_homeworld(x) for x in homeworld_urls}

        return etl.convert(table, "homeworld", homeworlds)

    def load_table(self, file: FieldFile) -> etl.Table:
        return etl.fromcsv(file)

    def aggregate(
        self, file: FieldFile, headers: list[str]
    ) -> list[dict[str, str | int]]:
        table = self.load_table(file)
        try:
            return list(etl.aggregate(table, headers, len).dicts())
        except etl.FieldSelectionError:
            raise StarWarsError("Invalid headers")

    def _fetch_homeworld(self, url: str) -> str:
        logger.debug(f"get world: {url}")
        response = requests.get(url)
        if not response.ok:
            raise StarWarsError(response.text)
        return response.json()["name"]


@dataclass
class CollectionService:
    repo: StarWarsAPI = field(default_factory=StarWarsAPI)
    character_etl: CharacterETL = field(default_factory=CharacterETL)

    def get_collection(self, collection_id: int) -> Collection:
        return Collection.objects.get(id=collection_id)

    @transaction.atomic
    def create_collection(self, table: etl.Table) -> Collection:
        filename = f"{uuid.uuid4().hex}.csv"
        collection = Collection()
        path = collection.file.storage.path(filename)
        table.tocsv(path)
        collection.file = path
        collection.save()

        characters_create = list()
        characters_list = table.list()
        fields = characters_list.pop(0)
        for row in characters_list:
            data = dict(zip(fields, row))
            data["date"] = parser.parse(data["date"]).date()
            character = Character(collection=collection, **data)
            characters_create.append(character)

        Character.objects.bulk_create(characters_create)
        return collection

    def export(self) -> Collection:
        data = self.repo.get_people()
        table = self.character_etl.transform(data)
        collection = self.create_collection(table)
        return collection

    def aggregate(
        self, collection: Collection, headers: list[str]
    ) -> list[dict[str, str | int]]:
        return self.character_etl.aggregate(collection.file, headers)
