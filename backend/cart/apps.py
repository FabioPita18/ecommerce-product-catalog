"""
Cart App Configuration.

This module configures the cart Django app.

App Configuration docs: https://docs.djangoproject.com/en/5.0/ref/applications/
"""

from django.apps import AppConfig


class CartConfig(AppConfig):
    """
    Configuration for the Cart app.

    Attributes:
        default_auto_field: Uses BigAutoField for auto-incrementing PKs
        name: Python path to the application
        verbose_name: Human-readable name for the admin interface
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "cart"
    verbose_name = "Shopping Cart"
