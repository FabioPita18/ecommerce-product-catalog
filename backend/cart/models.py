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

Why not store price in CartItem?
- Prices can change, and we want to show current price in cart
- Price at purchase time is stored in OrderItem instead (when checkout happens)
- This ensures cart always reflects current pricing

Django Model docs: https://docs.djangoproject.com/en/5.0/topics/db/models/
"""

from decimal import Decimal

from django.conf import settings
from django.db import models


class Cart(models.Model):
    """
    Shopping cart associated with a user.

    Each user has exactly one cart (OneToOneField). The cart is created
    automatically when the user adds their first item, and is cleared
    (items deleted) after successful order creation.

    Fields:
        user: OneToOne link to User model (using AUTH_USER_MODEL for flexibility)
        created_at: Timestamp when cart was created
        updated_at: Timestamp when cart was last modified (item added/removed/updated)

    Properties:
        total_items: Sum of all item quantities in the cart
        total_amount: Sum of all item subtotals (quantity × current price)

    Design Notes:
        - Using OneToOneField ensures one cart per user (enforced at DB level)
        - Cart itself has no price - calculated dynamically from items
        - Using settings.AUTH_USER_MODEL for portability (Django best practice)
        - related_name='cart' allows user.cart access
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        help_text="Cart owner. Each user has exactly one cart."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self) -> str:
        """Return string representation showing cart owner."""
        return f"Cart for {self.user.email}"

    @property
    def total_items(self) -> int:
        """
        Total number of items in cart (considering quantities).

        This is the sum of all item quantities, not the count of unique products.
        Example: 2 shirts + 3 pants = 5 total items.

        Returns:
            int: Total quantity of all items in cart
        """
        return sum(item.quantity for item in self.items.all())

    @property
    def total_amount(self) -> Decimal:
        """
        Total cart value (sum of all item subtotals).

        Calculated dynamically from current product prices. This ensures
        the cart always reflects current pricing - if a product price
        changes, the cart total updates automatically.

        Returns:
            Decimal: Total value of all items in cart
        """
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """
    Individual item in a shopping cart.

    Represents a product added to a cart with a specific quantity.
    The unique_together constraint ensures each product appears only
    once per cart - updating quantity instead of adding duplicate entries.

    Fields:
        cart: ForeignKey to parent Cart
        product: ForeignKey to the Product being purchased
        quantity: Number of items (must be positive)
        added_at: Timestamp when item was first added to cart
        updated_at: Timestamp when item was last modified (quantity change)

    Properties:
        subtotal: quantity × product.price (calculated dynamically)

    Constraints:
        - unique_together: (cart, product) - prevents duplicate product entries
        - quantity is PositiveIntegerField (enforces >= 0 at DB level)
        - Additional validation (>= 1, <= inventory) in serializer

    Design Notes:
        - Does NOT store price - uses current product price for calculations
        - Price at purchase time is captured in OrderItem during checkout
        - on_delete=CASCADE means removing cart removes items
        - related_name='items' allows cart.items.all()
        - related_name='cart_items' on Product allows product.cart_items.all()
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Parent cart containing this item"
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='cart_items',
        help_text="Product added to cart"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Number of items (must be at least 1)"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        # Ensure each product appears only once per cart
        # Adding same product again should update quantity, not create duplicate
        unique_together = ['cart', 'product']
        ordering = ['-added_at']

    def __str__(self) -> str:
        """Return string showing quantity and product name."""
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self) -> Decimal:
        """
        Calculate item subtotal (quantity × current price).

        Uses the product's current price, not a stored price.
        This ensures the cart always reflects up-to-date pricing.

        Returns:
            Decimal: Total value for this cart item
        """
        return self.product.price * self.quantity
