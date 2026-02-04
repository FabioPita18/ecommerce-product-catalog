"""
Order Serializers for Django REST Framework.

This module will contain serializers for:
- Order: The order container with status, totals, shipping info
- OrderItem: Individual items in the order (snapshot of product at purchase time)

Key Considerations:
- Orders are created from the current cart contents
- OrderItems store product info as a snapshot (price at time of purchase)
- Orders have status transitions: pending -> processing -> shipped -> delivered
- Totals include subtotal, tax, shipping, and grand total

Serializers to implement (Phase 5):
- OrderSerializer: Full order with nested items
- OrderItemSerializer: Individual order item
- OrderCreateSerializer: For checkout (converts cart to order)
- OrderListSerializer: Lightweight for order history

Example:
    class OrderSerializer(serializers.ModelSerializer):
        items = OrderItemSerializer(many=True, read_only=True)
        status_display = serializers.CharField(source='get_status_display', read_only=True)

        class Meta:
            model = Order
            fields = ['id', 'status', 'status_display', 'items', 'total', 'created_at']
"""
