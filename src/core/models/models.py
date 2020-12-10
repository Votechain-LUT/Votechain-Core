""" Module defining system's models """
from collections import namedtuple
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


User = get_user_model()


class Poll(models.Model):
    """ Represents a poll or election """
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=256, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    start = models.DateTimeField(blank=True, db_index=True, null=True)
    end = models.DateTimeField(blank=False)
    isActive = models.BooleanField(blank=False, default=False)


class Candidate(models.Model):
    """ Represents a candidate in an election or option in a poll """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500, blank=False)
    poll = models.ForeignKey(Poll, related_name="candidates", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("name", "poll"), name="UQ_Candidate_name_poll")
        ]


CandidateResult = namedtuple("CandidateResult", ["candidate", "number_of_votes"])


class Vote(models.Model):
    """ Used to represent a single vote """
    id = models.BigAutoField(primary_key=True)
    answer = models.ForeignKey(Candidate, on_delete=models.CASCADE)


class Voter(models.Model):
    """ Extends a built-in user model to define the relationship with polls """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    polls = models.ManyToManyField(Poll)


@receiver(post_save, sender=User)
def create_voter(sender, instance, created, **kwargs):
    """ Saves voter when user is added """
    if created:
        Voter.objects.create(user=instance)


@receiver(post_save, sender=User)
def update_voter(sender, instance, **kwargs):
    """ Updates voter when user is updated """
    instance.voter.save()
# pylint: enable=unused-argument


class Trail(models.Model):
    """ Used to track which users have already voted """
    id = models.BigAutoField(primary_key=True)
    trail_token = models.UUIDField(blank=False, auto_created=True)
    voter = models.OneToOneField(Voter, on_delete=models.CASCADE, blank=False)
    poll = models.OneToOneField(Poll, on_delete=models.CASCADE, blank=False)
