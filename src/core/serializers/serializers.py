""" Module defining serializers for models """
from django.contrib.auth import get_user_model
from rest_framework import serializers
from core.models.models import Candidate, Poll, Vote, Voter


User = get_user_model()


class CandidateNestedSerializer(serializers.ModelSerializer):
    """ Serializer for nested candidate model """
    class Meta:
        model = Candidate
        fields = ("id", "name")
        depth = 1


class PollSerializer(serializers.ModelSerializer):
    """ Serializer for poll model """
    candidates = CandidateNestedSerializer(many=True, read_only=True)
    class Meta:
        model = Poll
        fields = "__all__"
        depth = 1


class CandidateSerializer(serializers.ModelSerializer):
    """ Serializer for standalone candidate model """
    poll = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        queryset=Poll.objects.all()
        )

    class Meta:
        model = Candidate
        fields = "__all__"
        depth = 1


class VoteSerializer(serializers.ModelSerializer):
    """ Serializer for vote model """
    class Meta:
        model = Vote
        fields = "__all__"
        depth = 1
    answer = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    poll = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    def update(self, instance, validated_data):
        """ Do not allow updates """
        return instance


class VoterSerializer(serializers.ModelSerializer):
    """ Serializer for voter model """
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="email"
    )
    class Meta:
        model = Voter
        fields = "__all__"

    def update(self, instance, validated_data):
        return Voter.objects.update(**validated_data)
