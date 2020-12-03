from django.db import models
from django.contrib.auth.models import User

class Poll(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=256, blank=False)
    created = models.DateTimeField(auto_now=True)
    start = models.DateTimeField(blank=True, db_index=True, null=True)
    end = models.DateTimeField(blank=False)
    isActive = models.BooleanField(blank=False)

class Candidate(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    
class Candidate_result():

    def __init__(self, numberOfVotes:int, candidate: Candidate):
        self.numberOfVotes = numberOfVotes
        self.candidate = candidate
    
class Vote(models.Model):
    id = models.BigAutoField(primary_key=True)
    answer = models.ForeignKey(Candidate, on_delete=models.CASCADE)