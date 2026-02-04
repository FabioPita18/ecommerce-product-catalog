"""
Shopping Cart Models.

This module defines the data models for the shopping cart:
- Cart: Container for cart items, linked to a user
- CartItem: Individual item in the cart with quantity

Design Decisions:
- One cart per user (OneToOneField)
- CartItem uses unique_together to prevent duplicate product entries
- Quantity validation happens in serializers, not model
- Cart is created lazily when first item is added

Relationships:
- Cart -> User: OneToOne (each user has one cart)
- CartItem -> Cart: ForeignKey (cart has many items)
- CartItem -> Product: ForeignKey (item references a product)

Models will be implemented in Phase 4.
"""

from django.db import models  # noqa: F401

# Models will be implemented in Phase 4:
# - Cart
# - CartItem
#
# See CLAUDE.md in the backend directory for the model specifications.
