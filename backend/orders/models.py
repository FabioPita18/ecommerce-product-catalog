"""
Order Models.

This module defines the data models for order management:
- Order: Container for order items, with status, totals, shipping info
- OrderItem: Individual item in the order (snapshot of product at purchase)

Design Decisions:
- Orders have a status workflow: pending -> processing -> shipped -> delivered
- OrderItem stores price_at_purchase (price snapshot at order time)
- Cancellation is a status, not deletion (for audit trail)
- Orders are immutable after creation (no editing items)

Relationships:
- Order -> User: ForeignKey (user can have many orders)
- OrderItem -> Order: ForeignKey (order has many items)
- OrderItem -> Product: ForeignKey (for reference only, price is snapshotted)

Models will be implemented in Phase 5.
"""

from django.db import models  # noqa: F401

# Models will be implemented in Phase 5:
# - Order
# - OrderItem
#
# See CLAUDE.md in the backend directory for the model specifications.
