from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from core.serializers import jwt_serializers


JWT_REFRESH_COOKIE = "jwt_refresh"


class JwtAuthenticationView(TokenObtainPairView):
    serializer_class = jwt_serializers.JwtSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exception:
            raise InvalidToken(exception.args[0]) from exception
        token = serializer.get_token(serializer.user)
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        response.set_cookie(key=JWT_REFRESH_COOKIE, value=str(token), httponly=True)
        return response


class JwtRefreshView(TokenRefreshView):
    serializer_class = jwt_serializers.JwtRefreshSerializer

    def post(self, request, *args, **kwargs):
        token_payload = request.COOKIES.get(JWT_REFRESH_COOKIE)
        if token_payload is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={ "detail": JWT_REFRESH_COOKIE + " cookie is missing" }
            )
        serializer = self.get_serializer(data={ "refresh": token_payload })
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exception:
            raise InvalidToken(exception.args[0]) from exception
        token_str = serializer.validated_data["refresh"]
        serializer.validated_data.pop("refresh")
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        response.set_cookie(key=JWT_REFRESH_COOKIE, value=token_str, httponly=True)
        return response
