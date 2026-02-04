"""
URL Configuration for Products App.

This module defines URL patterns for product-related endpoints.
URLs are included in the main config/urls.py under the /api/products/ prefix.

URL Patterns (to be implemented in Phase 3):
    /api/products/                  - List products, create product
    /api/products/{id}/             - Retrieve, update, delete product
    /api/products/{slug}/           - Retrieve product by slug
    /api/products/featured/         - List featured products
    /api/products/search/?q=term    - Search products

DRF Routers docs: https://www.django-rest-framework.org/api-guide/routers/

Example:
    from rest_framework.routers import DefaultRouter
    from .views import ProductViewSet, CategoryViewSet

    router = DefaultRouter()
    router.register('products', ProductViewSet, basename='product')
    router.register('categories', CategoryViewSet, basename='category')

    urlpatterns = router.urls
"""

from django.urls import path  # noqa: F401

# Placeholder - will be replaced with router.urls in Phase 3
urlpatterns = []
