""" Module defining system's models """
from collections import namedtuple
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.db.models import F, Q
from django.dispatch import receiver
from django.utils import timezone
from django.core.signing import Signer, BadSignature


User = get_user_model()


class Poll(models.Model):
    """ Represents a poll or election """
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=256, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    start = models.DateTimeField(blank=True, db_index=True, null=True, default=timezone.now)
    end = models.DateTimeField(blank=False)
    isActive = models.BooleanField(blank=False, default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(end__gt=F('start')),
                name="core_poll_start_end_date_check"
            )
        ]

    def can_edit(self):
        """
        Checks whether the poll can be edited
        """
        datenow = timezone.now()
        if self.end < datenow:
            return False
        if self.start < datenow:
            return False
        return True

    def get_edit_status(self):
        """
        Checks whether the poll can be edited and why
        returns 0 when poll can be edited,
        1 when poll has already ended,
        -1 when poll has already started
        """
        datenow = timezone.now()
        if self.end < datenow:
            return 1
        if self.start < datenow:
            return -1
        return 0


class Candidate(models.Model):
    """ Represents a candidate in an election or option in a poll """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500, blank=False)
    poll = models.ForeignKey(Poll, related_name="candidates", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("name", "poll"), name="UQ_Candidate_name_poll")
        ]


CandidateResult = namedtuple(
    "CandidateResult",
    ["candidate_id", "candidate_name", "number_of_votes"]
)


class Vote(models.Model):
    """ Used to represent a single vote """
    id = models.BigAutoField(primary_key=True)
    answer = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(blank=False, auto_now_add=True)


class Voter(models.Model):
    """ Extends a built-in user model to define the relationship with polls """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    polls = models.ManyToManyField(Poll)
    password_changed = models.BooleanField(blank=False, default=False)


# pylint: disable=unused-argument
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
    """ Used to retrieve an associated vote """
    id = models.BigAutoField(primary_key=True)
    trail_token = models.UUIDField(blank=False, auto_created=True)
    vote = models.OneToOneField(Vote, on_delete=models.CASCADE, blank=False)

    @staticmethod
    def generate_token(vote, poll):
        """ generates a token for a given vote """
        token = uuid.uuid4()
        entity = Trail.objects.create(vote=vote, trail_token=token)
        payload = str(entity.trail_token) + '.' + str(poll.id) + '.' + str(entity.vote.id)
        return Signer().sign(payload)

    @staticmethod
    def decrypt(token):
        """ decrypts a vvpat token and returns its payload """
        try:
            payload = Signer().unsign(token)
        except BadSignature:
            return {}
        split = payload.split('.')
        return {
            "token": split[0],
            "poll_id": split[1],
            "vote_id": split[2]
        }


class VoteIdentificationToken(models.Model):
    """ Used to authorize a vote """
    id = models.BigAutoField(primary_key=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, blank=False)
    token = models.UUIDField(blank=False)
    assigned = models.BooleanField(blank=False, default=False)
    used = models.BooleanField(blank=False, default=False)

    @staticmethod
    def generate_token(poll):
        """ generates a token for a given poll """
        token = uuid.uuid4()
        entity = VoteIdentificationToken.objects.create(poll=poll, token=token)
        return entity

    def assign(self, email, connection):
        """ assigns a token to a user and send him an email """
        user = User.objects.filter(email=email).first()
        voter = None
        if user is not None:
            voter = Voter.objects.filter(user_id=user.id).first()
        if voter is not None:
            if self.poll in voter.polls.all():
                return False
            self.assigned = True
            voter.polls.add(self.poll)
            self.save()
            voter.save()
            return self._send_mail(email, connection=connection)
        return False

    def _send_mail(self, email, connection=None):
        """ Sends a vote identification token to an authorized user """
        message = """You have been authorized to take part in a poll titled:
{0}
Your authorization token is:
{1}""".format(self.poll.title, self.token)
        sent = 0
        sent = send_mail(
            'Votechain authentication token',
            message,
            'from@example.com',
            [email],
            fail_silently=False,
            connection=connection
        )
        return sent > 0

    def delete(self, using=None, keep_parents=False):
        pass
