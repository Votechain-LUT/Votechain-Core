from rest_framework import serializers
from core.models.models import Candidate, Poll, Vote
from django.contrib.auth.models import User

class PollSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, max_length=256)
    created = serializers.DateTimeField(required=False, read_only=True)
    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=True)
    isActive = serializers.BooleanField(required=True)
    
    def create(self, validated_data):
        return Poll.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.start = validated_data.get('start', instance.start)
        instance.end = validated_data.get('end', instance.end)
        instance.isActive = validated_data.get('isActive', instance.isActive)
        instance.save()
        return instance

class CandidateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50, required=True)
    poll = PollSerializer(many=True, read_only=True)

    def create(self, validated_data):
        return Candidate.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        return instance

class VoteSerializer(serializers.Serializer):
    answer = CandidateSerializer(many=True, read_only = True)
    poll = PollSerializer(many=True, read_only = True)

    def create(self, validated_data):
        return VoteSerializer.objects.create(**validated_data)

    
       