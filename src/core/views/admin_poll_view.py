""" Module containing views for administration panel """

from datetime import date
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status, generics, authentication, permissions
from core.models.models import Poll, Candidate
from core.serializers.serializers import PollSerializer, \
    CandidateSerializer, CandidateNestedSerializer


class AdminListOrCreatePoll(generics.ListCreateAPIView):
    """
    Lists all polls

    Optional query parameters:
    ongoing (true/false) - returns only ongoing polls
    future (true/false) - returns only future polls
    ended (true/false) - return only ended polls
    active (active/cancelled) - filter based on poll's cancellation status

    The date parameters are evaluated in order: ongoing, future, ended. If you specify both future
    and ended, only future polls will be returned.
    """
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        future = self.request.query_params.get("future", "False").lower() == "true"
        ongoing = self.request.query_params.get("ongoing", "False").lower() == "true"
        ended = self.request.query_params.get("ended", "False").lower() == "true"
        active = self.request.query_params.get("active", None)
        queryset = Poll.objects.all()
        if ongoing:
            queryset = queryset \
                .filter(start__lte=date.today()) \
                .filter(end__gte=date.today())
        elif future:
            queryset = queryset \
                .filter(start__gte=date.today())
        elif ended:
            queryset = queryset \
                .filter(end__lte=date.today())
        if active is not None:
            if active.lower() == "active":
                queryset = queryset.filter(isActive=True)
            elif active.lower() == "cancelled":
                queryset = queryset.filter(isActive=False)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AdminCreatePoll(generics.CreateAPIView):
    """ Creates a new poll """
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminPoll(generics.RetrieveUpdateAPIView):
    """ General poll management view """
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def get_queryset(self):
        poll_id = self.kwargs.get("id", None)
        return Poll.objects.filter(id=poll_id)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class AdminStartPoll(generics.GenericAPIView):
    """ View for starting a poll """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        """ Updates poll's start date to >>now<< """
        poll_id = self.kwargs.get("id", None)
        poll = Poll.objects.get(id=poll_id)
        datenow = timezone.now()
        if not poll:
            return Response(
                data="{ \"detail\": \"Poll not found\"}",
                status=status.HTTP_404_NOT_FOUND
            )
        if poll.end < datenow:
            return Response(
                data="{ \"detail\": \"Poll has already ended\"}",
                status=status.HTTP_400_BAD_REQUEST
            )
        if poll.start < datenow:
            return Response(
                data="{ \"detail\": \"Poll has already started\"}",
                status=status.HTTP_400_BAD_REQUEST
            )
        poll.start = datenow
        serializer = PollSerializer(instance=poll, many=False)
        poll.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminListOrAddCandidate(generics.ListCreateAPIView):
    """ View for listing or adding poll options """
    queryset = Candidate.objects.all()
    serializer_class = CandidateNestedSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        poll_id = self.kwargs.get("poll_id", None)
        return Candidate.objects.filter(poll=poll_id)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        poll_id = {"poll": self.kwargs.get("poll_id", None)}
        data = {**(request.data), **poll_id}
        serializer = CandidateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminGetDeleteCandidate(generics.RetrieveDestroyAPIView):
    """ View for managing poll options """
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def get_queryset(self):
        poll_id = self.kwargs.get("poll_id", None)
        candidate_id = self.kwargs.get(self.lookup_field, None)
        return Candidate.objects.filter(id=candidate_id, poll=poll_id)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
