"""
Views for the accounts app.

Contains:
    RegisterView – POST /api/auth/register/
    LoginView    – POST /api/auth/login/
"""

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """
    Register a new user and return an auth token.

    POST /api/auth/register/
    Body: {"username": "...", "email": "...", "password": "..."}

    Returns 201 on success with the user data and token.
    Returns 400 if validation fails (duplicate username, etc).
    """

    serializer_class = RegisterSerializer
    # Anyone can register — no authentication needed.
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create an auth token for the new user.
        token, _created = Token.objects.get_or_create(user=user)

        return Response(
            {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': token.key,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    Log in an existing user and return their auth token.

    POST /api/auth/login/
    Body: {"username": "...", "password": "..."}

    Returns 200 on success with the user data and token.
    Returns 400 if credentials are invalid.
    """

    # Anyone can attempt to log in.
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        # The LoginSerializer attaches the user to validated_data.
        user = serializer.validated_data['user']

        # get_or_create reuses the existing token if one exists,
        # so the user keeps the same token across logins.
        token, _created = Token.objects.get_or_create(user=user)

        return Response(
            {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': token.key,
            },
            status=status.HTTP_200_OK,
        )
