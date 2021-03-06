from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.utils import datetime_from_epoch
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model
from pytz import timezone
from votechain import settings


User = get_user_model()


class JwtSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        data["access"] = str(refresh.access_token)
        data["expires"] = str(
            datetime_from_epoch(refresh.access_token.payload["exp"])
                .astimezone(timezone(settings.TIME_ZONE))
        )
        data.pop("refresh")
        data["isAdmin"] = self.user.is_staff

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data

    def create(self, validated_data):
        raise NotImplementedError("No db action needed")

    def save(self, **kwargs):
        raise NotImplementedError("No db action needed")


class JwtRefreshSerializer(serializers.Serializer):
    def validate(self, attrs):
        refresh = RefreshToken(self.initial_data["refresh"])
        data = {}
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
        user = User.objects.filter(id=refresh.payload["user_id"]).first()
        if user is None:
            raise serializers.ValidationError(
                ("Invalid refresh token")
            )
        data["access"] = str(refresh.access_token)
        data["expires"] = str(
            datetime_from_epoch(refresh.access_token.payload["exp"])
                .astimezone(timezone(settings.TIME_ZONE))
        )
        data["refresh"] = str(refresh)
        data["isAdmin"] = user.is_staff
        return data

    def create(self, validated_data):
        raise NotImplementedError("No db action needed")

    def save(self, **kwargs):
        raise NotImplementedError("No db action needed")
