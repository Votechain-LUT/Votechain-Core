from rest_framework.response import Response
from rest_framework import status, generics, permissions
from core.models.models import Voter
from core.serializers.serializers import CompleteUserSerializer, PasswordSerializer, \
    VoterSerializer, UserSerializer


class BaseVoterView(generics.GenericAPIView):
    def get_queryset(self):
        return Voter.objects.filter(user=self.request.user)


class VoterView(BaseVoterView, generics.RetrieveAPIView):
    """ A view for voter to get his own data """
    serializer_class = CompleteUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, *args, **kwargs):
        voters = self.get_queryset()
        if voters.count() == 0:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"detail": "Could not retrieve voter's data"}
            )
        voter = voters.first()
        user_serial = UserSerializer(voter.user)
        voter_serial = VoterSerializer(voter)
        voter_serial.data.pop("user")
        return Response(
            data={ "user": user_serial.data, "voter": voter_serial.data},
            status=status.HTTP_200_OK
        )


class VoterChangePasswordView(BaseVoterView):
    """ A view for voter to change his password """
    serializer_class = PasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Voter.objects.filter(user=self.request.user)

    def put(self, *args, **kwargs):
        """ PUT method for changing the password """
        voter = self.get_queryset()
        if voter.count() == 0:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"detail": "Could not retrieve voter's data"}
            )
        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
