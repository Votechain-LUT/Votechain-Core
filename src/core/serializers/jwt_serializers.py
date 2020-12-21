from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.utils import datetime_from_epoch
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth.models import update_last_login


class JwtSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        data["access"] = str(refresh.access_token)
        data["expires"] = str(datetime_from_epoch(refresh.access_token.payload["exp"]))
        data.pop("refresh")

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
        data["access"] = str(refresh.access_token)
        data["expires"] = str(datetime_from_epoch(refresh.access_token.payload["exp"]))
        data["refresh"] = str(refresh)
        return data

    def create(self, validated_data):
        raise NotImplementedError("No db action needed")

    def save(self, **kwargs):
        raise NotImplementedError("No db action needed")
