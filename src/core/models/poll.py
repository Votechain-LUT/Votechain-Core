from django.db import models


class Poll(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=256, blank=False)
    created = models.DateTimeField(auto_now=True)
    start = models.DateTimeField(blank=True, db_index=True, null=True)
    end = models.DateTimeField(blank=False)
