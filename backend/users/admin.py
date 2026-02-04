"""
Django Admin Configuration for Users App.

This module registers the custom User model with Django admin.

Since we're using a custom User model with email as the identifier,
we need a custom UserAdmin that:
1. Doesn't reference the 'username' field
2. Uses 'email' as the identifier
3. Has appropriate fieldsets for our model

Django UserAdmin customization docs:
https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#a-full-example
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for the User model.

    This admin class is customized for our email-based User model.
    It inherits from Django's UserAdmin but overrides the fieldsets
    and display settings to work without a username field.

    Features:
    - List view shows email, name, active status, staff status
    - Filter by active, staff, and superuser status
    - Search by email and name
    - Proper fieldsets for user details, permissions, and dates
    """

    # =========================================================================
    # List View Configuration
    # =========================================================================

    # Fields to display in the list view
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "date_joined",
    )

    # Fields that can be clicked to view/edit the user
    list_display_links = ("email",)

    # Filters in the right sidebar
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    # Fields searchable via the search box
    search_fields = ("email", "first_name", "last_name")

    # Default ordering
    ordering = ("-date_joined",)

    # =========================================================================
    # Detail View Configuration (Fieldsets)
    # =========================================================================

    # Fieldsets for the change (edit) page
    # Each tuple is (title, {fields: [...]})
    fieldsets = (
        # No title for the main section
        (None, {"fields": ("email", "password")}),
        # Personal Info section
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        # Permissions section
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        # Important dates section
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # Fieldsets for the add (create) page
    # Simpler than the change page - just email and password
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),  # CSS class for wider display
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    # =========================================================================
    # Read-only Fields
    # =========================================================================

    # These fields cannot be edited
    readonly_fields = ("date_joined", "last_login")

    # =========================================================================
    # Filter Horizontal (Many-to-Many fields)
    # =========================================================================

    # Use a horizontal filter widget for these fields
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
