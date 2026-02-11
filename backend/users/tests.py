"""
Tests for User Authentication API.

Comprehensive tests for:
    - User registration (success, validation errors, duplicate email)
    - Login/logout (success, invalid credentials, token blacklisting)
    - Token refresh (success, invalid token)
    - Profile operations (view, update)
    - Password change (success, wrong current password, mismatch)

Testing Strategy:
    - Test both success and error cases
    - Test permission boundaries (authenticated vs unauthenticated)
    - Use pytest fixtures for test data setup

pytest-django docs: https://pytest-django.readthedocs.io/
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create a test user for login and profile tests."""
    return User.objects.create_user(
        email="testuser@example.com",
        password="TestPassword123!",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """
    Return an authenticated API client.

    Logs in via the login endpoint to get real JWT tokens,
    then sets the Authorization header.
    """
    response = api_client.post(
        reverse("users:login"),
        {"email": "testuser@example.com", "password": "TestPassword123!"},
        format="json",
    )
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
    )
    # Store the refresh token for logout tests
    api_client.refresh_token = response.data["refresh"]
    return api_client


# =============================================================================
# Registration Tests
# =============================================================================


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_success(self, api_client):
        """Successful registration returns 201 with tokens and user data."""
        url = reverse("users:register")
        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["email"] == "newuser@example.com"
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_register_duplicate_email(self, api_client, test_user):
        """Registration with existing email fails with 400."""
        url = reverse("users:register")
        data = {
            "email": "testuser@example.com",  # Already exists
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "Another",
            "last_name": "User",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_password_mismatch(self, api_client):
        """Registration with mismatched passwords fails."""
        url = reverse("users:register")
        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass123!",
            "first_name": "New",
            "last_name": "User",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data

    def test_register_weak_password(self, api_client):
        """Registration with weak password fails Django validation."""
        url = reverse("users:register")
        data = {
            "email": "newuser@example.com",
            "password": "123",  # Too short and common
            "password_confirm": "123",
            "first_name": "New",
            "last_name": "User",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_required_fields(self, api_client):
        """Registration without required fields fails."""
        url = reverse("users:register")
        data = {
            "email": "newuser@example.com",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =============================================================================
# Login Tests
# =============================================================================


@pytest.mark.django_db
class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success(self, api_client, test_user):
        """Successful login returns tokens and user data."""
        url = reverse("users:login")
        data = {
            "email": "testuser@example.com",
            "password": "TestPassword123!",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["email"] == "testuser@example.com"

    def test_login_wrong_password(self, api_client, test_user):
        """Login with wrong password fails with 401."""
        url = reverse("users:login")
        data = {
            "email": "testuser@example.com",
            "password": "WrongPassword123!",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        """Login with nonexistent email fails with 401."""
        url = reverse("users:login")
        data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Logout Tests
# =============================================================================


@pytest.mark.django_db
class TestUserLogout:
    """Test user logout endpoint."""

    def test_logout_success(self, authenticated_client):
        """Successful logout blacklists the refresh token."""
        url = reverse("users:logout")
        data = {"refresh": authenticated_client.refresh_token}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

    def test_logout_without_token(self, authenticated_client):
        """Logout without refresh token fails."""
        url = reverse("users:logout")

        response = authenticated_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_unauthenticated(self, api_client):
        """Logout without authentication fails with 401."""
        url = reverse("users:logout")

        response = api_client.post(
            url, {"refresh": "fake-token"}, format="json"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Token Refresh Tests
# =============================================================================


@pytest.mark.django_db
class TestTokenRefresh:
    """Test token refresh endpoint."""

    def test_refresh_success(self, api_client, test_user):
        """Successful token refresh returns new access token."""
        # First login to get tokens
        login_response = api_client.post(
            reverse("users:login"),
            {
                "email": "testuser@example.com",
                "password": "TestPassword123!",
            },
            format="json",
        )
        refresh_token = login_response.data["refresh"]

        # Refresh the token
        url = reverse("users:token-refresh")
        response = api_client.post(
            url, {"refresh": refresh_token}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_refresh_invalid_token(self, api_client):
        """Refresh with invalid token fails."""
        url = reverse("users:token-refresh")

        response = api_client.post(
            url, {"refresh": "invalid-token"}, format="json"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Profile Tests
# =============================================================================


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile endpoints."""

    def test_get_profile_success(self, authenticated_client):
        """Authenticated user can view their profile."""
        url = reverse("users:profile")

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "testuser@example.com"
        assert response.data["first_name"] == "Test"
        assert response.data["last_name"] == "User"

    def test_get_profile_unauthenticated(self, api_client):
        """Unauthenticated user cannot view profile."""
        url = reverse("users:profile")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_success(self, authenticated_client):
        """Authenticated user can update their profile."""
        url = reverse("users:profile")
        data = {
            "first_name": "Updated",
            "last_name": "Name",
        }

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify changes persisted
        profile_response = authenticated_client.get(url)
        assert profile_response.data["first_name"] == "Updated"
        assert profile_response.data["last_name"] == "Name"

    def test_update_profile_unauthenticated(self, api_client):
        """Unauthenticated user cannot update profile."""
        url = reverse("users:profile")
        data = {"first_name": "Hacker"}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Password Change Tests
# =============================================================================


@pytest.mark.django_db
class TestPasswordChange:
    """Test password change endpoint."""

    def test_password_change_success(self, authenticated_client, test_user):
        """Successful password change updates the password."""
        url = reverse("users:password-change")
        data = {
            "current_password": "TestPassword123!",
            "new_password": "NewSecurePass456!",
            "new_password_confirm": "NewSecurePass456!",
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify old password no longer works and new one does
        test_user.refresh_from_db()
        assert not test_user.check_password("TestPassword123!")
        assert test_user.check_password("NewSecurePass456!")

    def test_password_change_wrong_current(self, authenticated_client):
        """Password change with wrong current password fails."""
        url = reverse("users:password-change")
        data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewSecurePass456!",
            "new_password_confirm": "NewSecurePass456!",
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_change_mismatch(self, authenticated_client):
        """Password change with mismatched new passwords fails."""
        url = reverse("users:password-change")
        data = {
            "current_password": "TestPassword123!",
            "new_password": "NewSecurePass456!",
            "new_password_confirm": "DifferentPass789!",
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_change_unauthenticated(self, api_client):
        """Unauthenticated user cannot change password."""
        url = reverse("users:password-change")
        data = {
            "current_password": "TestPassword123!",
            "new_password": "NewSecurePass456!",
            "new_password_confirm": "NewSecurePass456!",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
