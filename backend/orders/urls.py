"""
URL Configuration for Orders App.

This module defines URL patterns for order-related endpoints.
URLs are included in the main config/urls.py under the /api/orders/ prefix.

URL Patterns:
    GET    /api/orders/         - List user's orders (order history)
    POST   /api/orders/         - Create order (checkout from cart)
    GET    /api/orders/{id}/    - View order details

Design Notes:
    - All order endpoints require JWT authentication
    - Users can only access their own orders
    - Order creation (POST) triggers the checkout process
    - URL patterns do NOT include 'orders/' prefix because config/urls.py
      already maps /api/orders/ to this module via include()
    - Using simple path() instead of a router because we only have
      two views (list+create and detail)

Django URL docs: https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.urls import path

from .views import OrderDetailView, OrderListCreateView

# App namespace for URL reversing: reverse('orders:order-list')
app_name = "orders"

urlpatterns = [
    # List orders (GET) and create order / checkout (POST)
    path("", OrderListCreateView.as_view(), name="order-list"),
    # View order details (GET)
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
]
