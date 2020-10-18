from django.http import Http404
from rest_framework.response import Response
from rest_framework import status, generics, authentication, permissions
from core.models.poll import Poll
from core.serializers.poll_serializer import PollSerializer


class AdminListPoll(generics.ListAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication
    ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AdminCreatePoll(generics.CreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication
    ]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AdminPoll(generics.RetrieveUpdateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication
    ]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class AdminStartPoll(generics.GenericAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, pk):
        from datetime import datetime
        poll = Poll.objects.get(pk=pk)
        poll.start = datetime.now()
        serializer = self.get_serializer(data=poll, many=False)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
