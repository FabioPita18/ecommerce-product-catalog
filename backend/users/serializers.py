"""
User Serializers for Django REST Framework.

Handles serialization for:
    - User registration (with password validation)
    - User profile (read-only view)
    - User profile update (writable fields)
    - Password change (requires current password)
    - Token response (for API documentation)

Security Notes:
    - Password fields are always write_only (never exposed in responses)
    - Django's built-in password validators enforce strength requirements
    - Email uniqueness is enforced at the database level
    - Passwords are hashed using Django's PBKDF2 hasher (never stored plain)

DRF Serializers docs: https://www.django-rest-framework.org/api-guide/serializers/
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# get_user_model() returns the active User model (our custom one).
# This is the recommended way to reference the User model - never import it directly.
User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates:
        - Email uniqueness (database-level + serializer-level)
        - Password strength (Django's built-in validators)
        - Password confirmation match

    On success, the view generates JWT tokens so the user is
    immediately logged in after registration.
    """

    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with this email already exists.",
            )
        ],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
        ]

    def validate(self, attrs):
        """Validate that password and password_confirm match."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """
        Create user with hashed password.

        Uses create_user() which properly hashes the password.
        Removes password_confirm since it's not a model field.
        """
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing user profile.

    All fields are read-only except first_name and last_name.
    Used for GET /api/auth/profile/ and nested in token responses.

    Why read-only for email?
        Email changes should go through a separate verification flow
        (send confirmation email to new address) to prevent account hijacking.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "email", "date_joined", "last_login"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.

    Only allows updating non-sensitive fields (first_name, last_name).
    Email and password changes have dedicated endpoints with extra security.
    """

    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.

    Requires the current password for verification before allowing change.
    This prevents someone with a stolen access token from locking out the user.

    Flow:
        1. User submits current_password + new_password + new_password_confirm
        2. We verify current_password matches
        3. We validate new_password strength
        4. We verify new_password matches new_password_confirm
        5. We update the password
    """

    current_password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
    )

    def validate_current_password(self, value):
        """Verify the current password is correct before allowing change."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        return attrs

    def save(self):
        """Update the user's password."""
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer for token response documentation.

    This serializer is not used for data processing - it's used by
    drf-spectacular to generate accurate API documentation for endpoints
    that return JWT tokens.
    """

    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    user = UserProfileSerializer(help_text="User profile data")
