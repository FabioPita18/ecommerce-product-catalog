"""
Order API Views.

Provides endpoints for order management:
    GET    /api/orders/         - List user's orders (order history)
    POST   /api/orders/         - Create order (checkout from cart)
    GET    /api/orders/{id}/    - View order details

All order endpoints require authentication.
Users can only view their own orders.

Checkout Process (POST /api/orders/):
    1. Validate user has items in cart
    2. Validate shipping address is provided
    3. Validate inventory is available for ALL cart items
    4. Create Order with calculated total
    5. Create OrderItems with price snapshots
    6. Decrement product inventory
    7. Clear the cart
    8. Return the created order

The entire checkout is wrapped in @transaction.atomic to ensure
data consistency - if any step fails, everything is rolled back.

DRF Views docs: https://www.django-rest-framework.org/api-guide/views/
"""

from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart

from .models import Order, OrderItem
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)


class OrderListCreateView(APIView):
    """
    List user's orders and create new orders (checkout).

    GET  /api/orders/   - List all orders for the authenticated user
    POST /api/orders/   - Create a new order from cart contents (checkout)

    Why APIView instead of ViewSet?
        - Only two operations needed (list + create)
        - Checkout logic is complex and doesn't fit standard create pattern
        - More explicit control over the checkout flow
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List orders",
        description="Get the authenticated user's order history.",
        responses={200: OrderListSerializer(many=True)},
    )
    def get(self, request):
        """Return all orders for the authenticated user, newest first."""
        orders = Order.objects.filter(user=request.user).order_by(
            "-created_at"
        )
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create order (checkout)",
        description=(
            "Create a new order from the user's cart contents. "
            "Validates inventory, creates order items with price snapshots, "
            "decrements inventory, and clears the cart."
        ),
        request=OrderCreateSerializer,
        responses={
            201: OrderDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    @transaction.atomic
    def post(self, request):
        """
        Checkout: Convert cart contents to an order.

        This is the core checkout flow:
        1. Validate input (shipping address)
        2. Get user's cart and validate it has items
        3. Check inventory for all items
        4. Create the order and order items
        5. Decrement product inventory
        6. Clear the cart
        7. Return the created order

        Everything is wrapped in @transaction.atomic so if any step
        fails (e.g., insufficient inventory), the entire operation
        is rolled back and no data is changed.
        """
        # Step 1: Validate input
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2: Get cart and validate it has items
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = cart.items.select_related("product").all()

        if not cart_items.exists():
            return Response(
                {"detail": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 3: Validate inventory for ALL items before creating anything
        # This prevents partial orders where some items succeed and others fail
        inventory_errors = []
        for item in cart_items:
            if not item.product.is_active:
                inventory_errors.append(
                    f"{item.product.name} is no longer available."
                )
            elif item.quantity > item.product.inventory_count:
                inventory_errors.append(
                    f"Only {item.product.inventory_count} of "
                    f"{item.product.name} available "
                    f"(requested {item.quantity})."
                )

        if inventory_errors:
            return Response(
                {"detail": inventory_errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 4: Calculate total and create order
        total_amount = sum(
            item.product.price * item.quantity for item in cart_items
        )

        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            shipping_address=serializer.validated_data["shipping_address"],
            notes=serializer.validated_data.get("notes", ""),
            status=Order.Status.PENDING,
        )

        # Step 5: Create order items with price snapshots and decrement inventory
        order_items = []
        for item in cart_items:
            order_items.append(
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price,
                )
            )
            # Decrement inventory
            item.product.inventory_count -= item.quantity
            item.product.save(update_fields=["inventory_count"])

        # Bulk create order items for efficiency
        OrderItem.objects.bulk_create(order_items)

        # Step 6: Clear the cart
        cart.items.all().delete()

        # Step 7: Return the created order
        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
    """
    View order details.

    GET /api/orders/{id}/

    Returns full order information including all items.
    Users can only view their own orders.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get order details",
        description="Retrieve full details of a specific order.",
        responses={
            200: OrderDetailSerializer,
            404: OpenApiResponse(description="Order not found"),
        },
    )
    def get(self, request, pk):
        """Return order details, ensuring it belongs to the authenticated user."""
        order = get_object_or_404(Order, pk=pk, user=request.user)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)


class OrderCancelView(APIView):
    """
    Cancel a pending order.

    POST /api/orders/{id}/cancel/

    Only orders with 'pending' status can be cancelled.
    Cancelling restores inventory for all order items.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Cancel order",
        description=(
            "Cancel a pending order. Restores product inventory "
            "for all items in the order."
        ),
        request=None,
        responses={
            200: OrderDetailSerializer,
            400: OpenApiResponse(description="Order cannot be cancelled"),
            404: OpenApiResponse(description="Order not found"),
        },
    )
    @transaction.atomic
    def post(self, request, pk):
        """
        Cancel the order and restore inventory.

        Only pending orders can be cancelled. Processing/shipped/delivered
        orders require a different workflow (returns, refunds, etc.).
        """
        order = get_object_or_404(Order, pk=pk, user=request.user)

        if order.status != Order.Status.PENDING:
            return Response(
                {"detail": "Only pending orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Restore inventory for each order item
        for item in order.items.select_related("product").all():
            item.product.inventory_count += item.quantity
            item.product.save(update_fields=["inventory_count"])

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])

        return Response(OrderDetailSerializer(order).data)
