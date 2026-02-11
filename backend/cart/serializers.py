"""
Cart Serializers for Django REST Framework.

Handles serialization for:
    - Cart items (view, add, update, remove)
    - Cart summary (with totals)

Design Notes:
    - Cart is created lazily when the first item is added
    - Cart items reference products by ID for writes, nest product data for reads
    - Quantities are validated against product inventory
    - Prices are NOT stored in cart - always uses current product price

DRF Serializers docs: https://www.django-rest-framework.org/api-guide/serializers/
"""

from rest_framework import serializers

from products.models import Product
from products.serializers import ProductListSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for reading cart items.

    Includes nested product details and computed subtotal so the frontend
    can display cart contents without extra API calls.
    """

    product = ProductListSerializer(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "subtotal"]
        read_only_fields = ["id", "subtotal"]


class CartItemCreateSerializer(serializers.Serializer):
    """
    Serializer for adding items to cart.

    Validates:
        - Product exists and is active
        - Product is in stock
        - Requested quantity doesn't exceed inventory
    """

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        """Validate product exists and is active."""
        try:
            Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                "Product not found or unavailable."
            )
        return value

    def validate(self, attrs):
        """Validate stock availability for the requested quantity."""
        product = Product.objects.get(id=attrs["product_id"])

        if not product.is_in_stock:
            raise serializers.ValidationError(
                {"product_id": "Product is out of stock."}
            )

        if attrs["quantity"] > product.inventory_count:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        f"Only {product.inventory_count} items available."
                    )
                }
            )

        # Attach product object for use in the view
        attrs["product"] = product
        return attrs


class CartItemUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating cart item quantity.

    Validates the new quantity against available inventory.
    The cart_item is passed via serializer context.
    """

    quantity = serializers.IntegerField(min_value=1)

    def validate_quantity(self, value):
        """Validate quantity against product inventory."""
        cart_item = self.context.get("cart_item")
        if cart_item and value > cart_item.product.inventory_count:
            raise serializers.ValidationError(
                f"Only {cart_item.product.inventory_count} items available."
            )
        return value


class CartSerializer(serializers.ModelSerializer):
    """
    Full cart serializer with nested items and computed totals.

    Used for GET /api/cart/ to display the complete cart contents.
    """

    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = ["id", "items", "total_items", "total_amount", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class CartSummarySerializer(serializers.Serializer):
    """
    Lightweight cart summary for header/badge display.

    Only includes count and total - no item details.
    Useful for showing cart icon badge without loading full cart.
    """

    total_items = serializers.IntegerField()
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2
    )
