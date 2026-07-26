"""
Serializers for the accounts app.

Contains:
    RegisterSerializer – Validates and creates a new user.
    LoginSerializer    – Validates credentials for login.
"""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles user registration.

    Accepts username, email, and password.
    Password is write-only so it never appears in responses.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text='Must be at least 8 characters.',
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        read_only_fields = ['id']

    def validate_username(self, value):
        """Reject usernames that are blank or only whitespace."""
        if not value.strip():
            raise serializers.ValidationError(
                'Username cannot be blank.'
            )
        return value.strip()

    def validate_email(self, value):
        """Reject blank emails and check for duplicates."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                'Email is required.'
            )
        value = value.strip().lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'A user with this email already exists.'
            )
        return value

    def create(self, validated_data):
        """
        Use create_user() instead of create() so the password
        gets hashed properly.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Validates login credentials.

    This is a plain Serializer (not ModelSerializer) because we
    are not creating or updating a model — just checking credentials.
    """

    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        """
        Use Django's authenticate() to check the credentials.
        If they are wrong, raise a validation error.
        """
        username = attrs.get('username', '').strip()
        password = attrs.get('password', '')

        if not username or not password:
            raise serializers.ValidationError(
                'Both username and password are required.'
            )

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                'Invalid username or password.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This account has been disabled.'
            )

        # Attach the user to validated_data so the view can use it.
        attrs['user'] = user
        return attrs
