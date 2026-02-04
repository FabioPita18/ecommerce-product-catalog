"""
Products App Configuration.

This module configures the products Django app.

App Configuration docs: https://docs.djangoproject.com/en/5.0/ref/applications/
"""

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """
    Configuration for the Products app.

    Attributes:
        default_auto_field: Uses BigAutoField for auto-incrementing PKs
            (supports larger IDs than AutoField, recommended for new projects)
        name: Python path to the application
        verbose_name: Human-readable name for the admin interface
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "products"
    verbose_name = "Product Catalog"
