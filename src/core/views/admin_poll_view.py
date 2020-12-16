""" Module containing views for administration panel """

from django.utils import timezone
from django.db.utils import IntegrityError
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from core.models.models import Poll, Candidate
from core.serializers.serializers import PollSerializer, \
    CandidateSerializer, CandidateNestedSerializer


def update_poll(request, poll, method, *args, **kwargs):
    if poll.can_edit():
        return method(request, *args, **kwargs)
    poll_status = poll.get_edit_status()
    if poll_status == 1:
        return Response(
            data={ "detail": "Poll has already ended"},
            status=status.HTTP_400_BAD_REQUEST
        )
    if poll_status == -1:
        return Response (
            data={ "detail": "Cannot edit an ongoing poll"},
            status=status.HTTP_400_BAD_REQUEST
        )

class AdminListOrCreatePoll(generics.ListCreateAPIView):
    """
    Lists or creates polls
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
        datenow = timezone.now()
        if ongoing:
            queryset = queryset \
                .filter(start__lte=datenow) \
                .filter(end__gte=datenow)
        elif future:
            queryset = queryset \
                .filter(start__gte=datenow)
        elif ended:
            queryset = queryset \
                .filter(end__lte=datenow)
        if active is not None:
            if active.lower() == "true":
                queryset = queryset.filter(isActive=True)
            elif active.lower() == "false":
                queryset = queryset.filter(isActive=False)
        return queryset

    def get(self, request, *args, **kwargs):
        """
        Optional query parameters:
        ongoing (true/false) - returns only ongoing polls
        future (true/false) - returns only future polls
        ended (true/false) - return only ended polls
        active (true/false) - filter based on poll's cancellation status

        The date parameters are evaluated in order: ongoing, future, ended. If you specify both future
        and ended, only future polls will be returned.
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """ Creates a new poll """
        return self.create(request, *args, **kwargs)


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
        if self.get_queryset().count() > 0:
            return update_poll(request, self.get_queryset()[0], self.update, *args, **kwargs)
        return Response(
            data={ "detail": "Poll not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    def patch(self, request, *args, **kwargs):
        if self.get_queryset().count() > 0:
            return update_poll(request, self.get_queryset()[0], self.update, *args, **kwargs)
        return Response(
            data={ "detail": "Poll not found"},
            status=status.HTTP_404_NOT_FOUND
        )


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
                data={ "detail": "Poll not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        if poll.end < datenow:
            return Response(
                data={ "detail": "Poll has already ended"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if poll.start < datenow:
            return Response(
                data={ "detail": "Poll has already started"},
                status=status.HTTP_400_BAD_REQUEST
            )
        poll.start = datenow
        poll.isActive = True
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
        poll = Poll.objects.get(id=poll_id["poll"])
        if poll is None:
            return Response(
                data={ "detail": "Poll not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CandidateSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if poll.can_edit():
            try:
                serializer.save()
            except IntegrityError:
                return Response(
                    data={"detail": "Candidate already exists in this poll" },
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(serializer.data)
        return update_poll(request, poll, None, *args, **kwargs)

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
        if self.get_queryset().count() > 0:
            return update_poll(request, self.get_queryset()[0].poll, self.destroy, *args, **kwargs)
        return Response(
            data={ "detail": "Poll not found"},
            status=status.HTTP_404_NOT_FOUND
        )
