"""
Cart Serializers for Django REST Framework.

This module will contain serializers for:
- Cart: The shopping cart container
- CartItem: Individual items in the cart

Key Considerations:
- Cart is tied to a user (authenticated) or session (anonymous)
- CartItem includes quantity and references a Product
- Serializers must handle inventory validation
- Price calculations happen server-side for security

Serializers to implement (Phase 4):
- CartSerializer: Full cart with nested items
- CartItemSerializer: Individual cart item
- CartItemCreateSerializer: For adding items to cart
- CartItemUpdateSerializer: For updating quantity

Example:
    class CartItemSerializer(serializers.ModelSerializer):
        product = ProductListSerializer(read_only=True)
        subtotal = serializers.DecimalField(read_only=True)

        class Meta:
            model = CartItem
            fields = ['id', 'product', 'quantity', 'subtotal']
"""
