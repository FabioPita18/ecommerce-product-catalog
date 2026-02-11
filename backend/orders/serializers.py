"""
Order Serializers for Django REST Framework.

Handles serialization for:
    - Order items (with price snapshot from purchase time)
    - Orders (list, detail, create via checkout)

Design Notes:
    - OrderItem stores price_at_purchase (snapshot, not current product price)
    - OrderCreateSerializer handles the checkout process:
      1. Validates cart has items
      2. Validates inventory for all items
      3. Creates order + order items in a single transaction
      4. Decrements inventory
      5. Clears the cart
    - Orders are read-only after creation (items cannot be edited)
    - Status changes are the only updates allowed

DRF Serializers docs: https://www.django-rest-framework.org/api-guide/serializers/
"""

from rest_framework import serializers

from products.serializers import ProductListSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for reading order items.

    Includes nested product details and the price at time of purchase.
    The subtotal is computed from price_at_purchase × quantity, NOT
    from the current product price.

    Why include both product and price_at_purchase?
        - product: For linking to product pages, showing images, etc.
        - price_at_purchase: For accurate order history (product price may change)
    """

    product = ProductListSerializer(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "quantity",
            "price_at_purchase",
            "subtotal",
        ]
        read_only_fields = ["id", "price_at_purchase", "subtotal"]


class OrderListSerializer(serializers.ModelSerializer):
    """
    Lightweight order serializer for list views.

    Used for GET /api/orders/ to display order history.
    Includes only summary information - no nested items.
    The frontend can click through to the detail view for full info.

    Why a separate list serializer?
        - Listing many orders with nested items is expensive
        - Order history page only needs summary data
        - Detail endpoint provides the full picture
    """

    item_count = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "status_display",
            "total_amount",
            "item_count",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "total_amount",
            "item_count",
            "created_at",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Full order serializer with nested items.

    Used for GET /api/orders/{id}/ to display complete order details.
    Includes all order items with product info and price snapshots.
    """

    items = OrderItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "status_display",
            "items",
            "total_amount",
            "item_count",
            "shipping_address",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "total_amount",
            "item_count",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer for creating an order (checkout).

    The checkout process converts the user's cart into an order:
    1. Validates the cart has items
    2. Validates inventory for all cart items
    3. Accepts shipping address and optional notes

    The actual order creation (with inventory decrement and cart clearing)
    happens in the view, wrapped in a database transaction.

    Why a plain Serializer instead of ModelSerializer?
        - The input (shipping_address, notes) is simple
        - The creation logic is complex (multi-model, inventory checks)
        - Better to keep complex logic in the view where it's explicit
    """

    shipping_address = serializers.CharField(
        max_length=500,
        help_text="Delivery address for the order",
    )
    notes = serializers.CharField(
        max_length=500,
        required=False,
        default="",
        help_text="Optional notes or special instructions",
    )
