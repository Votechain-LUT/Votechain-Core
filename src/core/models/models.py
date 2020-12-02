from django.db import models
from django.contrib.auth.models import User

class Poll(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=256, blank=False)
    created = models.DateTimeField(auto_now=True)
    start = models.DateTimeField(blank=True, db_index=True, null=True)
    end = models.DateTimeField(blank=False)

class Voter(models.Model):
    id = models.BigAutoField(primary_key=True)


class Vote(models.Model):
    answer = models.TextField(max_length=1024, blank=False)
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.models.ForeignKey(Poll, on_delete=models.CASCADE)



class Canidate(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    poll = models.ForeignKey (Poll, on_delete=models.CASCADE)
    
 

class Candidate_result(models.Model):
    numberOfVotes = models.BigAutoField()
    candidate = models.models.ForeignKey(Candidate, on_delete=models.CASCADE)