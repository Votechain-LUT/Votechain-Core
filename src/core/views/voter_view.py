""" Module containing views for administration panel """

import json
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework import status, generics, permissions
from drf_yasg.utils import swagger_auto_schema
from core.models.models import Poll, Voter, Candidate, Trail, VoteIdentificationToken
from core.serializers.serializers import PollSerializer, TokenSerializer
from core.validators import is_vit_valid
from core.views.admin_poll_view import ongoing_param, ended_param
from votechain.hyperledger import VotechainNetworkClient


def save_vote(candidate, poll, vit):
    """ Saves a cast vote """
    votechain_client = VotechainNetworkClient()
    response = votechain_client.cast_vote(poll.id, candidate.name)
    parsed_response = json.loads(response)
    token = Trail.generate_token(parsed_response["txId"])
    vit.used = True
    vit.save()
    return TokenSerializer(data={"token": token})


class VoterView(generics.GenericAPIView):
    """ Base view for voter views filtering polls based on authorized user """
    def get_queryset(self):
        voter = Voter.objects.filter(user=self.request.user).first()
        if voter is None:
            return Poll.objects.none()
        if self.request.user.is_superuser:
            return Poll.objects.all()
        return voter.polls


class VoterListPoll(generics.ListAPIView, VoterView):
    """
    Lists polls
    """
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        ongoing = self.request.query_params.get("ongoing", "False").lower() == "true"
        ended = self.request.query_params.get("ended", "False").lower() == "true"
        datenow = timezone.now()
        if ongoing:
            queryset = queryset \
                .filter(start__lte=datenow) \
                .filter(end__gte=datenow)
        elif ended:
            queryset = queryset \
                .filter(end__lte=datenow)
        return queryset

    @swagger_auto_schema(manual_parameters=[ongoing_param, ended_param])
    def get(self, request, *args, **kwargs):
        """
        Optional query parameters:
        ongoing -- (true/false) returns only ongoing polls
        ended -- (true/false) return only ended polls

        The date parameters are evaluated in order: ongoing, ended. If you specify both ongoing
        and ended, only ongoing polls will be returned.
        """
        return self.list(request, *args, **kwargs)

class VoterCastVote(generics.CreateAPIView, VoterView):
    """
    Casts votes to a given poll
    """
    serializer_class = TokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def are_params_valid(self, poll, candidate, vit):
        """ validates endpoint parameters """
        if poll is None:
            return False, Response(
                data={ "detail": "Poll doesn't exist" },
                status=status.HTTP_404_NOT_FOUND
            )
        if candidate is None or candidate not in poll.candidates.all():
            return False, Response(
                data={ "detail": "Candidate doesn't exist" },
                status=status.HTTP_404_NOT_FOUND
            )
        if vit is None:
            return False, Response(
                data={ "detail": "VIT is missing" },
                status=status.HTTP_401_UNAUTHORIZED
            )
        datenow = timezone.now()
        if poll.start > datenow:
            return False, Response(
                data={ "detail": "Voting has not started yet" },
                status=status.HTTP_400_BAD_REQUEST
            )
        if poll.end < datenow:
            return False, Response(
                data={ "detail": "Voting has already ended" },
                status=status.HTTP_400_BAD_REQUEST
            )
        return True, None

    def post(self, request, *args, **kwargs):
        """
        Casts a vote
        """
        poll_id = self.kwargs.get("poll_id", None)
        poll = self.get_queryset().filter(id=poll_id).first()
        candidate_id = self.kwargs.get("candidate_id", None)
        candidate = Candidate.objects.filter(id=candidate_id).first()
        token = self.request.data.get("token")
        vit = VoteIdentificationToken.objects.filter(token=token).first()
        valid, response = self.are_params_valid(poll, candidate, vit)
        if not valid:
            return response
        if not is_vit_valid(vit, poll):
            return Response(
                data={ "detail": "Token does not exist" },
                status=status.HTTP_401_UNAUTHORIZED
            )
        vvpat = save_vote(candidate, poll, vit)
        return Response(
            status=status.HTTP_201_CREATED,
            data=vvpat.initial_data
        )

class VoterGetVote(generics.CreateAPIView, VoterView):
    """ Verifies a vote """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TokenSerializer

    def post(self, request, *args, **kwargs):
        """
        Gets a vote for an ended poll
        """
        poll_id = self.kwargs.get("poll_id", None)
        datenow = timezone.now()
        poll = self.get_queryset().filter(id=poll_id).first()
        if poll is None:
            return Response(
                data={ "detail": "Poll doesn't exist" },
                status=status.HTTP_404_NOT_FOUND
            )
        vvpat = self.request.data.get("token")
        if vvpat is None:
            return Response(
                data={"detail": "VVPAT for verification is missing"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if poll.end > datenow:
            return Response(
                data={"detail": "Voting hasn't ended yet"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        token = Trail.decrypt(vvpat)
        if not token:
            return Response(
                data={"detail": "Token does not exist"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        votechain_client = VotechainNetworkClient()
        response = votechain_client.verify_vote(poll_id, token)
        if response is None:
            return Response(
                data={"detail": "Vote not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        parsed_response = json.loads(response)
        candidate = parsed_response.get("candidate", None)
        if candidate is None:
            return Response(
                data={"detail": "Vote not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
                data={ "candidate_name": candidate },
                status=status.HTTP_200_OK
            )

class VoterGetResults(generics.RetrieveAPIView, VoterView):
    serializer_class = Serializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        datenow = timezone.now()
        poll_id = self.kwargs.get("poll_id", None)
        poll = self.get_queryset().filter(id=poll_id).first()
        if poll is None:
            return Response(
                data={ "detail": "Poll doesn't exist" },
                status=status.HTTP_404_NOT_FOUND
            )
        if poll.end > datenow:
            return Response(
                data={"detail": "Voting hasn't ended yet"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        result = []
        votechain_client = VotechainNetworkClient()
        response = votechain_client.get_results(poll_id)
        if response is None:
            return Response(
                data={"detail": "Vote not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        result = json.loads(response)
        http_status = status.HTTP_404_NOT_FOUND if len(result) == 0 else status.HTTP_200_OK
        return Response(
            status=http_status,
            data={"results": result}
        )
