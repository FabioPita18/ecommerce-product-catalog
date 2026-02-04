"""
Order Models for E-Commerce Platform.

This module defines the data models for order management:
- Order: Container for order items, with status, totals, shipping info
- OrderItem: Individual item in the order (snapshot of product at purchase)

Order Lifecycle (Status Workflow):
1. pending - Order just created, awaiting processing
2. processing - Payment confirmed, preparing for shipment
3. shipped - Order has been shipped to customer
4. delivered - Order received by customer
5. cancelled - Order was cancelled (can happen from pending/processing)

Design Decisions:
- Store price_at_purchase in OrderItem (price snapshot at order time)
- Shipping address as text field (simple approach for MVP, no address model)
- Total amount calculated at checkout and stored (not computed each time)
- Orders are immutable after creation (items cannot be edited)
- Cancellation is a status, not deletion (maintains audit trail)

Relationships:
- Order -> User: ForeignKey (user can have many orders)
- OrderItem -> Order: ForeignKey (order has many items)
- OrderItem -> Product: ForeignKey (for reference, price is snapshotted)

Django Model docs: https://docs.djangoproject.com/en/5.0/topics/db/models/
"""

from decimal import Decimal

from django.conf import settings
from django.db import models


class Order(models.Model):
    """
    Customer order containing one or more items.

    Created from cart contents during checkout. An order represents a
    complete purchase transaction with shipping information and status tracking.

    Order Status Flow:
        pending -> processing -> shipped -> delivered
              \\-> cancelled (can cancel from pending or processing)

    Fields:
        user: ForeignKey to User (customer who placed the order)
        status: Current order status (from Status choices)
        total_amount: Total order value (calculated and stored at checkout)
        shipping_address: Delivery address as text
        notes: Optional customer notes or special instructions
        created_at: Timestamp when order was placed
        updated_at: Timestamp when order was last modified

    Properties:
        item_count: Total number of items in order (sum of quantities)

    Design Notes:
        - total_amount is stored, not calculated, for performance and audit
        - Orders are immutable after creation (can't add/remove items)
        - Status changes are the only allowed updates
        - Using TextChoices for type-safe status values
        - Indexes on user+status for "my orders" queries and status for "shipped"
    """

    class Status(models.TextChoices):
        """
        Order status choices using Django's TextChoices.

        TextChoices provides:
        - Type safety with IDE autocomplete
        - Automatic form widget support
        - Human-readable labels for admin/API
        """
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="Customer who placed this order"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="Current order status"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total order amount (calculated and stored at checkout)"
    )
    shipping_address = models.TextField(
        help_text="Delivery address for this order"
    )
    notes = models.TextField(
        blank=True,
        help_text="Customer notes or special instructions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            # Composite index for "my orders" page (user's orders by status)
            models.Index(fields=['user', 'status']),
            # Index for admin order management (filter by date)
            models.Index(fields=['-created_at']),
        ]

    def __str__(self) -> str:
        """Return string showing order ID and customer email."""
        return f"Order #{self.id} - {self.user.email}"

    @property
    def item_count(self) -> int:
        """
        Total number of items in order (considering quantities).

        Returns:
            int: Sum of all order item quantities
        """
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """
    Individual item in an order (snapshot of product at purchase).

    OrderItem stores the price at the time of purchase because:
    - Product prices can change after the order is placed
    - Need historical accuracy for accounting and reporting
    - Customer should see what they actually paid
    - Refunds need to reference original purchase price

    Fields:
        order: ForeignKey to parent Order
        product: ForeignKey to Product (for reference/linking)
        quantity: Number of items purchased
        price_at_purchase: Product price when order was placed

    Properties:
        subtotal: quantity × price_at_purchase

    Design Notes:
        - Unlike CartItem, this DOES store price (snapshot at checkout)
        - Product FK is kept for reference but price is independent
        - If product is deleted, order item remains (historical data)
        - on_delete=CASCADE for product means items deleted if product deleted
          (In production, you might use SET_NULL to preserve order history)
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Parent order containing this item"
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='order_items',
        help_text="Product that was purchased"
    )
    quantity = models.PositiveIntegerField(
        help_text="Number of items purchased"
    )
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Product price at time of purchase (snapshot)"
    )

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self) -> str:
        """Return string showing quantity and product name."""
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self) -> Decimal:
        """
        Calculate item subtotal using price at purchase time.

        Unlike CartItem.subtotal which uses current price,
        this uses the stored price_at_purchase for accuracy.

        Returns:
            Decimal: Total value for this order item
        """
        return self.price_at_purchase * self.quantity
