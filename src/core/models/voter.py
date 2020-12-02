from django.db import models


class Voter(models.Model):
    id = models.BigAutoField(primary_key=True)
