from functools import update_wrapper
from django.contrib.auth import get_user_model
from django.http import Http404
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics, permissions
from core.models.models import Voter
from core.serializers.serializers import UserSerializer, VoterSerializer


UserModel = get_user_model()


def admin_view(view, cacheable=False):
    """
    Overwrite the default admin view to return 404 for not logged in users.
    """
    def inner(request, *args, **kwargs):
        if not request.user.is_active and not request.user.is_staff:
            raise Http404()
        return view(request, *args, **kwargs)

    if not cacheable:
        inner = never_cache(inner)

    # We add csrf_protect here so this function can be used as a utility
    # function for any view, without having to repeat 'csrf_protect'.
    if not getattr(view, 'csrf_exempt', False):
        inner = csrf_protect(inner)

    return update_wrapper(inner, view)

class RegisterVoterView(generics.CreateAPIView):
    queryset = UserModel.objects.all()
    permission_classes = [
        permissions.IsAdminUser
    ]
    serializer_class = UserSerializer


class GetVoterView(generics.RetrieveAPIView):
    queryset = Voter.objects.all()
    permission_classes = [
        permissions.IsAdminUser
    ]
    serializer_class = VoterSerializer

class ChangePasswordView(generics.UpdateAPIView):
    queryset = Voter.objects.all()
    peprmission_classes = [permissions.IsAuthenticated]
