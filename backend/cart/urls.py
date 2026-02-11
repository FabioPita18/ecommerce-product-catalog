"""
URL Configuration for Cart App.

This module defines URL patterns for shopping cart endpoints.
URLs are included in the main config/urls.py under the /api/cart/ prefix.

URL Patterns:
    GET    /api/cart/              - View cart with all items and totals
    DELETE /api/cart/              - Clear entire cart
    GET    /api/cart/summary/      - Lightweight cart summary (count + total)
    POST   /api/cart/items/        - Add item to cart
    PATCH  /api/cart/items/{id}/   - Update item quantity
    DELETE /api/cart/items/{id}/   - Remove item from cart

Design Notes:
    - All cart endpoints require JWT authentication
    - Cart is created lazily (get_or_create) when first item is added
    - Using APIView instead of ViewSets because cart operations don't
      map cleanly to standard CRUD (no list/create/update on cart itself)
    - URL patterns do NOT include 'cart/' prefix because config/urls.py
      already maps /api/cart/ to this module via include()

Django URL docs: https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.urls import path

from .views import CartItemDetailView, CartItemListView, CartSummaryView, CartView

# App namespace for URL reversing: reverse('cart:cart')
app_name = "cart"

urlpatterns = [
    # Cart overview: GET to view, DELETE to clear
    path("", CartView.as_view(), name="cart"),
    # Lightweight summary for header badge display
    path("summary/", CartSummaryView.as_view(), name="cart-summary"),
    # Add items to cart (POST)
    path("items/", CartItemListView.as_view(), name="cart-items"),
    # Update (PATCH) or remove (DELETE) a specific cart item
    path(
        "items/<int:pk>/",
        CartItemDetailView.as_view(),
        name="cart-item-detail",
    ),
]
