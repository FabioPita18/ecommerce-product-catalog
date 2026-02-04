"""
URL Configuration for Cart App.

This module defines URL patterns for shopping cart endpoints.
URLs are included in the main config/urls.py under the /api/cart/ prefix.

URL Patterns (to be implemented in Phase 4):
    /api/cart/                  - Get current user's cart
    /api/cart/items/            - Add item to cart
    /api/cart/items/{id}/       - Update/remove cart item
    /api/cart/clear/            - Clear all items from cart

Design Notes:
- Cart endpoints require authentication (JWT)
- Anonymous carts can be merged with user cart on login
- Inventory is validated when adding/updating items

Example:
    urlpatterns = [
        path('', CartView.as_view(), name='cart-detail'),
        path('items/', CartItemListCreateView.as_view(), name='cart-items'),
        path('items/<int:pk>/', CartItemDetailView.as_view(), name='cart-item-detail'),
        path('clear/', CartClearView.as_view(), name='cart-clear'),
    ]
"""

from django.urls import path  # noqa: F401

# Placeholder - will be implemented in Phase 4
urlpatterns = []
