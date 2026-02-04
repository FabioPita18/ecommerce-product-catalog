"""
URL Configuration for Users App.

This module defines URL patterns for authentication and user management.
URLs are included in the main config/urls.py under the /api/auth/ prefix.

URL Patterns (to be implemented in Phase 4):
    /api/auth/register/         - User registration
    /api/auth/login/            - Get JWT tokens (access + refresh)
    /api/auth/refresh/          - Refresh access token
    /api/auth/logout/           - Blacklist refresh token
    /api/auth/user/             - Get/update current user profile
    /api/auth/password/change/  - Change password

JWT Authentication Flow:
1. User registers or logs in
2. Server returns access token (short-lived) and refresh token (long-lived)
3. Client includes access token in Authorization header: "Bearer <token>"
4. When access token expires, client uses refresh token to get new access token
5. On logout, refresh token is blacklisted

simplejwt docs: https://django-rest-framework-simplejwt.readthedocs.io/

Example:
    from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

    urlpatterns = [
        path('register/', UserRegistrationView.as_view(), name='register'),
        path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('user/', UserProfileView.as_view(), name='user-profile'),
    ]
"""

from django.urls import path  # noqa: F401

# Placeholder - will be implemented in Phase 4
urlpatterns = []
