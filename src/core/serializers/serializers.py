from rest_framework import serializers
from core.models.models import Poll, Candidate, Candidate_result, Vote


class PollSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, max_length=256)
    created = serializers.DateTimeField(required=False, read_only=True)
    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=True)

    def create(self, validated_data):
        return Poll.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.start = validated_data.get('start', instance.start)
        instance.end = validated_data.get('end', instance.end)
        instance.save()
        return instance