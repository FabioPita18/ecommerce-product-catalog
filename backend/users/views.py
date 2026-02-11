"""
User Authentication and Profile API Views.

Provides endpoints for:
    - User registration (with automatic JWT token generation)
    - Login (JWT token obtain via email + password)
    - Logout (blacklist refresh token)
    - Token refresh (exchange refresh token for new access token)
    - Profile view and update
    - Password change

JWT Authentication Flow:
    1. User registers (POST /api/auth/register/) -> receives tokens
    2. User logs in (POST /api/auth/login/) -> receives tokens
    3. Client sends access token with requests: "Authorization: Bearer <token>"
    4. When access token expires, refresh it (POST /api/auth/refresh/)
    5. On logout, blacklist refresh token (POST /api/auth/logout/)

DRF Views docs: https://www.django-rest-framework.org/api-guide/views/
simplejwt docs: https://django-rest-framework-simplejwt.readthedocs.io/
"""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    PasswordChangeSerializer,
    TokenResponseSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user account.

    POST /api/auth/register/

    Creates a new user and returns JWT tokens for immediate login.
    No authentication required (anyone can register).

    Request body:
        - email: Valid email address (must be unique)
        - password: Strong password (validated by Django)
        - password_confirm: Must match password
        - first_name: User's first name
        - last_name: User's last name

    Response (201):
        - access: JWT access token (use in Authorization header)
        - refresh: JWT refresh token (use to get new access tokens)
        - user: User profile data
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register new user",
        description="Create a new user account. Returns JWT tokens on success.",
        responses={
            201: TokenResponseSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the new user so they're immediately logged in
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint - obtain JWT token pair.

    POST /api/auth/login/

    Authenticates with email and password, returns access and refresh
    tokens along with user profile data.

    Request body:
        - email: User's email address
        - password: User's password

    Response (200):
        - access: JWT access token
        - refresh: JWT refresh token
        - user: User profile data
    """

    @extend_schema(
        summary="User login",
        description="Authenticate with email and password. Returns JWT tokens.",
        responses={
            200: TokenResponseSerializer,
            401: OpenApiResponse(description="Invalid credentials"),
        },
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Add user profile data to the token response
            user = User.objects.get(email=request.data["email"])
            response.data["user"] = UserProfileSerializer(user).data

        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Refresh access token.

    POST /api/auth/refresh/

    Exchange a valid refresh token for a new access token.
    If ROTATE_REFRESH_TOKENS is True (our config), also returns
    a new refresh token and blacklists the old one.

    Request body:
        - refresh: Valid refresh token

    Response (200):
        - access: New JWT access token
        - refresh: New JWT refresh token (if rotation enabled)
    """

    @extend_schema(
        summary="Refresh access token",
        description="Exchange a valid refresh token for a new access token.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """
    Logout endpoint - blacklist refresh token.

    POST /api/auth/logout/

    Blacklists the provided refresh token so it can't be used to
    get new access tokens. The client should also delete stored tokens.

    Why blacklisting?
        JWT tokens are stateless - the server can't "invalidate" them.
        By blacklisting the refresh token, we prevent new access tokens
        from being issued. Existing access tokens will expire naturally.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="User logout",
        description=(
            "Blacklist the refresh token. "
            "Client should also delete stored tokens."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh": {
                        "type": "string",
                        "description": "Refresh token to blacklist",
                    }
                },
                "required": ["refresh"],
            }
        },
        responses={
            200: OpenApiResponse(description="Successfully logged out"),
            400: OpenApiResponse(
                description="Invalid or missing refresh token"
            ),
        },
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except TokenError:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile endpoint.

    GET   /api/auth/profile/    - View profile
    PUT   /api/auth/profile/    - Full update
    PATCH /api/auth/profile/    - Partial update

    Users can only access their own profile (get_object returns request.user).
    """

    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the authenticated user's profile."""
        return self.request.user

    def get_serializer_class(self):
        """Use different serializer for read vs write."""
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserProfileSerializer

    @extend_schema(
        summary="Get user profile",
        description="Retrieve the authenticated user's profile.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update user profile",
        description="Update the authenticated user's profile fields.",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update user profile",
        description="Partially update the authenticated user's profile.",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PasswordChangeView(APIView):
    """
    Change password endpoint.

    POST /api/auth/password/change/

    Requires the current password for verification.
    This prevents someone with a stolen access token from
    changing the password and locking out the real user.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change password",
        description=(
            "Change the authenticated user's password. "
            "Requires current password verification."
        ),
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )
