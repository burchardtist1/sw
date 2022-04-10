from django.db import models


class Collection(models.Model):
    file = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)


class Character(models.Model):
    collection = models.ForeignKey(
        "Collection", on_delete=models.CASCADE, related_name="characters"
    )

    name = models.CharField(max_length=255)
    height = models.CharField(max_length=255)
    mass = models.CharField(max_length=255)
    hair_color = models.CharField(max_length=255)
    skin_color = models.CharField(max_length=255)
    eye_color = models.CharField(max_length=255)
    birth_year = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    homeworld = models.CharField(max_length=255)
    date = models.DateField()
