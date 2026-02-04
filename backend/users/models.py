"""
Custom User Model.

This module defines a custom User model that uses email as the username.

Why a Custom User Model?
-----------------------------------------------------------------
Django's default User model uses 'username' as the unique identifier.
Modern applications typically use email for authentication because:
1. Users already remember their email
2. Email is unique and verifiable
3. Enables password reset via email

IMPORTANT: The custom User model MUST be defined BEFORE running any migrations.
Once migrations are created with AUTH_USER_MODEL pointing here, changing
the User model becomes very difficult.

Custom User Model docs:
https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#specifying-a-custom-user-model

Design Decisions:
-----------------------------------------------------------------
- Email is the unique identifier (USERNAME_FIELD)
- No username field at all (cleaner than making it optional)
- AbstractBaseUser for full control (vs AbstractUser which has username)
- PermissionsMixin adds is_superuser, groups, permissions
- Custom UserManager for create_user() and create_superuser()
"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom manager for User model with email as the unique identifier.

    This manager provides methods for creating regular users and superusers.
    It's required when using AbstractBaseUser.

    Why a Custom Manager?
    -----------------------------------------------------------------
    AbstractBaseUser doesn't have a default create_user() method.
    We need to define how users are created, especially:
    - Normalizing email (lowercase)
    - Hashing passwords
    - Setting is_staff/is_superuser for admin users

    BaseUserManager docs:
    https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.

        Args:
            email: User's email address (required)
            password: User's password (optional, but recommended)
            **extra_fields: Additional fields (first_name, last_name, etc.)

        Returns:
            User: The created user instance

        Raises:
            ValueError: If email is not provided

        Example:
            user = User.objects.create_user(
                email='user@example.com',
                password='securepass123',
                first_name='John',
                last_name='Doe'
            )
        """
        if not email:
            raise ValueError(_("The Email field must be set"))

        # Normalize email: lowercase the domain part
        # john@EXAMPLE.COM -> john@example.com
        email = self.normalize_email(email)

        # Set default values for regular users
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        # Create the user instance
        user = self.model(email=email, **extra_fields)

        # set_password() hashes the password using Django's password hashers
        # Never store plain text passwords!
        user.set_password(password)

        # Save to database
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.

        Superusers have full access to Django admin and all permissions.

        Args:
            email: Superuser's email address
            password: Superuser's password
            **extra_fields: Additional fields

        Returns:
            User: The created superuser instance

        Raises:
            ValueError: If is_staff or is_superuser is False

        Example:
            python manage.py createsuperuser
            # Or programmatically:
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123'
            )
        """
        # Superusers must have these flags set
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Validate the flags
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email as the unique identifier.

    This model replaces Django's default User model. It uses email
    for authentication instead of username.

    Inheritance:
    -----------------------------------------------------------------
    - AbstractBaseUser: Provides password hashing and token generation
    - PermissionsMixin: Adds is_superuser, groups, user_permissions

    Fields:
    -----------------------------------------------------------------
    - email: Primary identifier, must be unique
    - first_name, last_name: Optional profile information
    - is_active: Can the user log in?
    - is_staff: Can access Django admin?
    - date_joined: When the account was created

    Relationships (to be added in later phases):
    -----------------------------------------------------------------
    - Cart: OneToOne (each user has one cart)
    - Orders: ForeignKey (user can have many orders)

    Usage:
    -----------------------------------------------------------------
    # Get the User model (recommended way)
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Create a user
    user = User.objects.create_user(
        email='user@example.com',
        password='pass123',
        first_name='John'
    )

    # Check password
    user.check_password('pass123')  # True
    """

    # ==========================================================================
    # Fields
    # ==========================================================================

    email = models.EmailField(
        _("email address"),
        unique=True,
        help_text=_("Required. A valid email address."),
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    first_name = models.CharField(
        _("first name"),
        max_length=150,
        blank=True,
        help_text=_("Optional. User's first name."),
    )

    last_name = models.CharField(
        _("last name"),
        max_length=150,
        blank=True,
        help_text=_("Optional. User's last name."),
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    date_joined = models.DateTimeField(
        _("date joined"),
        default=timezone.now,
        help_text=_("The date and time when the user registered."),
    )

    # ==========================================================================
    # Manager
    # ==========================================================================

    objects = UserManager()

    # ==========================================================================
    # Authentication Configuration
    # ==========================================================================

    # The field used as the unique identifier for authentication
    USERNAME_FIELD = "email"

    # Fields required when creating a superuser via createsuperuser command
    # (email is already required as USERNAME_FIELD)
    REQUIRED_FIELDS = []

    # ==========================================================================
    # Meta Options
    # ==========================================================================

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    # ==========================================================================
    # Methods
    # ==========================================================================

    def __str__(self) -> str:
        """Return the email as the string representation."""
        return self.email

    def get_full_name(self) -> str:
        """
        Return the first_name plus the last_name, with a space in between.

        Returns:
            str: Full name or email if no name is set
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    def get_short_name(self) -> str:
        """
        Return the short name for the user.

        Returns:
            str: First name or email if no name is set
        """
        return self.first_name if self.first_name else self.email
