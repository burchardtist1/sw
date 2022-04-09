from django.db import models


class Collection(models.Model):
    file = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
