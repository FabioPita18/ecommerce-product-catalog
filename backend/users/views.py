"""
User Authentication and Profile API Views.

This module will contain views for:
- RegisterView: User registration
- UserProfileView: Get/update current user profile
- PasswordChangeView: Change password

JWT Authentication Views (from simplejwt):
- TokenObtainPairView: Login, returns access + refresh tokens
- TokenRefreshView: Refresh access token using refresh token
- TokenBlacklistView: Logout, blacklist refresh token

JWT Flow:
1. User registers (POST /api/auth/register/)
2. User logs in (POST /api/auth/login/) -> receives tokens
3. Client includes access token in requests: "Authorization: Bearer <token>"
4. When access token expires, refresh it (POST /api/auth/refresh/)
5. On logout, blacklist refresh token (POST /api/auth/logout/)

Views will be implemented in Phase 4.
"""

# Views will be implemented in Phase 4
# Example structure:
#
# from rest_framework import generics
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework_simplejwt.views import TokenObtainPairView
#
# class RegisterView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = UserCreateSerializer
#
# class UserProfileView(generics.RetrieveUpdateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserSerializer
#
#     def get_object(self):
#         return self.request.user
