"""
Cart API Views.

Provides endpoints for shopping cart management:
    GET    /api/cart/              - View cart with all items and totals
    DELETE /api/cart/              - Clear entire cart
    GET    /api/cart/summary/      - Lightweight cart summary (count + total)
    POST   /api/cart/items/        - Add item to cart
    PATCH  /api/cart/items/{id}/   - Update item quantity
    DELETE /api/cart/items/{id}/   - Remove item from cart

All cart endpoints require authentication.
Cart is created automatically when the first item is added.

DRF Views docs: https://www.django-rest-framework.org/api-guide/views/
"""

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import (
    CartItemCreateSerializer,
    CartItemSerializer,
    CartItemUpdateSerializer,
    CartSerializer,
    CartSummarySerializer,
)


class CartView(APIView):
    """
    View and manage the user's cart.

    GET /api/cart/     - View cart with all items, totals
    DELETE /api/cart/  - Clear entire cart (removes all items)
    """

    permission_classes = [IsAuthenticated]

    def get_or_create_cart(self, user):
        """Get existing cart or create a new empty one."""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    @extend_schema(
        summary="Get cart",
        description="Retrieve the authenticated user's shopping cart with all items.",
        responses={200: CartSerializer},
    )
    def get(self, request):
        """Return the user's cart with items and totals."""
        cart = self.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        summary="Clear cart",
        description="Remove all items from the cart.",
        responses={204: OpenApiResponse(description="Cart cleared")},
    )
    def delete(self, request):
        """Remove all items from the cart."""
        cart = self.get_or_create_cart(request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartSummaryView(APIView):
    """
    Lightweight cart summary for header/badge display.

    GET /api/cart/summary/

    Returns only the item count and total amount - no item details.
    Useful for displaying a cart badge in the navigation bar.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get cart summary",
        description="Get lightweight cart summary (count and total).",
        responses={200: CartSummarySerializer},
    )
    def get(self, request):
        """Return cart summary with count and total."""
        try:
            cart = Cart.objects.get(user=request.user)
            data = {
                "total_items": cart.total_items,
                "total_amount": cart.total_amount,
            }
        except Cart.DoesNotExist:
            data = {
                "total_items": 0,
                "total_amount": "0.00",
            }

        serializer = CartSummarySerializer(data)
        return Response(serializer.data)


class CartItemListView(APIView):
    """
    Add items to cart.

    POST /api/cart/items/

    If the product is already in the cart, the quantity is increased
    rather than creating a duplicate entry.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add item to cart",
        description=(
            "Add a product to the cart. "
            "If already in cart, increases quantity."
        ),
        request=CartItemCreateSerializer,
        responses={
            201: CartItemSerializer,
            200: CartItemSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    @transaction.atomic
    def post(self, request):
        """Add item to cart or increase quantity if already present."""
        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get or create cart for this user
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        # Check if product already in cart
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            # Product already in cart - increase quantity
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.inventory_count:
                return Response(
                    {
                        "detail": (
                            f"Only {product.inventory_count} items available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            cart_item.quantity = new_quantity
            cart_item.save()
            response_status = status.HTTP_200_OK
        except CartItem.DoesNotExist:
            # New product - create cart item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity,
            )
            response_status = status.HTTP_201_CREATED

        return Response(
            CartItemSerializer(cart_item).data,
            status=response_status,
        )


class CartItemDetailView(APIView):
    """
    Update or remove a cart item.

    PATCH  /api/cart/items/{id}/  - Update quantity
    DELETE /api/cart/items/{id}/  - Remove item from cart

    Users can only modify their own cart items.
    """

    permission_classes = [IsAuthenticated]

    def get_cart_item(self, request, pk):
        """Get cart item ensuring it belongs to the authenticated user."""
        return get_object_or_404(
            CartItem, pk=pk, cart__user=request.user
        )

    @extend_schema(
        summary="Update cart item",
        description="Update the quantity of a cart item.",
        request=CartItemUpdateSerializer,
        responses={
            200: CartItemSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Cart item not found"),
        },
    )
    @transaction.atomic
    def patch(self, request, pk):
        """Update cart item quantity."""
        cart_item = self.get_cart_item(request, pk)

        serializer = CartItemUpdateSerializer(
            data=request.data, context={"cart_item": cart_item}
        )
        serializer.is_valid(raise_exception=True)

        cart_item.quantity = serializer.validated_data["quantity"]
        cart_item.save()

        return Response(CartItemSerializer(cart_item).data)

    @extend_schema(
        summary="Remove cart item",
        description="Remove an item from the cart.",
        responses={
            204: OpenApiResponse(description="Item removed"),
            404: OpenApiResponse(description="Cart item not found"),
        },
    )
    def delete(self, request, pk):
        """Remove an item from the cart."""
        cart_item = self.get_cart_item(request, pk)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
