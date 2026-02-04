"""
Orders App Configuration.

This module configures the orders Django app.

App Configuration docs: https://docs.djangoproject.com/en/5.0/ref/applications/
"""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """
    Configuration for the Orders app.

    Attributes:
        default_auto_field: Uses BigAutoField for auto-incrementing PKs
        name: Python path to the application
        verbose_name: Human-readable name for the admin interface
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"
    verbose_name = "Order Management"
