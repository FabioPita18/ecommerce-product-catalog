"""
User Authentication URL Configuration.

All authentication endpoints are prefixed with /api/auth/ (configured in config/urls.py).

Endpoints:
    POST /api/auth/register/          - Create new user account
    POST /api/auth/login/             - Get JWT tokens (access + refresh)
    POST /api/auth/logout/            - Blacklist refresh token
    POST /api/auth/refresh/           - Exchange refresh token for new access token
    GET  /api/auth/profile/           - View user profile
    PUT  /api/auth/profile/           - Update user profile
    PATCH /api/auth/profile/          - Partial update user profile
    POST /api/auth/password/change/   - Change password

JWT Authentication Flow:
    1. Register or login to get tokens
    2. Include access token in Authorization header: "Bearer <token>"
    3. When access token expires, use refresh token to get a new one
    4. On logout, blacklist the refresh token

simplejwt docs: https://django-rest-framework-simplejwt.readthedocs.io/
"""

from django.urls import path

from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    PasswordChangeView,
    UserProfileView,
    UserRegistrationView,
)

# app_name creates a namespace for URL reversing: reverse('users:login')
app_name = "users"

urlpatterns = [
    # Registration
    path("register/", UserRegistrationView.as_view(), name="register"),
    # Login/Logout
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Token refresh
    path("refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    # Profile
    path("profile/", UserProfileView.as_view(), name="profile"),
    # Password
    path(
        "password/change/",
        PasswordChangeView.as_view(),
        name="password-change",
    ),
]
