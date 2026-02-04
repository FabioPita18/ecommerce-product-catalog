"""
URL Configuration for Orders App.

This module defines URL patterns for order-related endpoints.
URLs are included in the main config/urls.py under the /api/orders/ prefix.

URL Patterns (to be implemented in Phase 5):
    /api/orders/                - List user's orders, create order (checkout)
    /api/orders/{id}/           - Retrieve order details

Design Notes:
- All order endpoints require authentication
- Users can only see their own orders
- Creating an order (POST /api/orders/) triggers the checkout process:
  1. Validates cart has items
  2. Validates inventory is available
  3. Creates Order and OrderItems
  4. Decrements inventory
  5. Clears the cart
  6. Returns created order

Example:
    from rest_framework.routers import DefaultRouter
    from .views import OrderViewSet

    router = DefaultRouter()
    router.register('', OrderViewSet, basename='order')

    urlpatterns = router.urls
"""

from django.urls import path  # noqa: F401

# Placeholder - will be implemented in Phase 5
urlpatterns = []
