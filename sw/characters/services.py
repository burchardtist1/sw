import logging
import os
import uuid
from dataclasses import dataclass, field
from typing import Any

import petl as etl
import requests
from django.conf import settings
from django.db.models.fields.files import FieldFile
from faker import Faker
from rest_framework.serializers import ValidationError

from characters.models import Collection

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
                "height": self.fake.name(),
                "mass": "100",
                "hair_color": self.fake.name(),
                "skin_color": self.fake.name(),
                "eye_color": self.fake.name(),
                "birth_year": self.fake.name(),
                "gender": self.fake.name(),
                "homeworld": self.fake.name(),
            }
        ] * 3


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
    ]

    def save(self, data: CharactersListTyping) -> str:
        table = etl.fromdicts(data, header=self.header)

        file_path = os.path.join(settings.MEDIA_ROOT, f"{uuid.uuid4().hex}.csv")
        table.tocsv(file_path)
        return file_path

    def aggregate(
        self, file: FieldFile, headers: list[str]
    ) -> list[dict[str, str | int]]:
        table = etl.fromcsv(file)
        try:
            return list(etl.aggregate(table, headers, len).dicts())
        except etl.FieldSelectionError:
            raise StarWarsError("Invalid headers")


@dataclass
class CollectionService:
    repo: StarWarsAPI = field(default_factory=StarWarsAPI)
    character_etl: CharacterETL = field(default_factory=CharacterETL)

    def get_collection(self, collection_id: int) -> Collection:
        return Collection.objects.get(id=collection_id)

    def create_collection(self, data: CharactersListTyping) -> Collection:
        csv_file = self.character_etl.save(data)
        return Collection.objects.create(file=csv_file)

    def export(self) -> Collection:
        data = self.repo.get_people()

        homeworlds = dict()
        for person in data:
            homeworld_url = person["homeworld"]
            try:
                homeworld = homeworlds[homeworld_url]
            except KeyError:
                homeworld = self._fetch_homeworld(homeworld_url)
                logger.debug(f"new world: {homeworld}")
                homeworlds[homeworld_url] = homeworld

            person["homeworld"] = homeworld

        collection = self.create_collection(data)
        return collection

    def aggregate(
        self, collection: Collection, headers: list[str]
    ) -> list[dict[str, str | int]]:
        return self.character_etl.aggregate(collection.file, headers)

    def _fetch_homeworld(self, url: str) -> str:
        response = requests.get(url)
        if not response.ok:
            raise StarWarsError(response.text)
        return response.json()["name"]
