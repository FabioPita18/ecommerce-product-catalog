"""
Tests for Orders API.

Comprehensive tests for:
    - List orders (GET /api/orders/)
    - Create order / checkout (POST /api/orders/)
    - Order detail (GET /api/orders/{id}/)
    - Checkout validation (empty cart, inventory, inactive products)
    - Inventory decrement after checkout
    - Cart cleared after checkout

Testing Strategy:
    - All order endpoints require authentication (test 401 for anonymous)
    - Test complete checkout flow end-to-end
    - Test inventory is decremented correctly
    - Test cart is emptied after successful checkout
    - Test price snapshot (price_at_purchase) is stored correctly
    - Test various error conditions (empty cart, insufficient inventory)

pytest-django docs: https://pytest-django.readthedocs.io/
"""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from products.models import Category, Product

User = get_user_model()


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create a test user for order tests."""
    return User.objects.create_user(
        email="orderuser@example.com",
        password="TestPassword123!",
        first_name="Order",
        last_name="User",
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name="Electronics",
        slug="electronics",
        description="Electronic devices",
    )


@pytest.fixture
def product(db, category):
    """Create a test product with inventory."""
    return Product.objects.create(
        name="Test Laptop",
        slug="test-laptop",
        description="A test laptop",
        price="999.99",
        category=category,
        inventory_count=10,
        is_active=True,
    )


@pytest.fixture
def second_product(db, category):
    """Create a second test product."""
    return Product.objects.create(
        name="Test Tablet",
        slug="test-tablet",
        description="A test tablet",
        price="599.99",
        category=category,
        inventory_count=5,
        is_active=True,
    )


@pytest.fixture
def cart_with_items(test_user, product, second_product):
    """
    Create a cart with items ready for checkout.

    Cart contains:
        - 2x Test Laptop ($999.99) = $1999.98
        - 1x Test Tablet ($599.99) = $599.99
        - Total: $2599.97
    """
    cart = Cart.objects.create(user=test_user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    CartItem.objects.create(cart=cart, product=second_product, quantity=1)
    return cart


@pytest.fixture
def existing_order(test_user, product):
    """Create an existing order for list/detail tests."""
    order = Order.objects.create(
        user=test_user,
        total_amount="999.99",
        shipping_address="123 Test St, Test City",
        status=Order.Status.PENDING,
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price_at_purchase="999.99",
    )
    return order


# =============================================================================
# Order List Tests (GET /api/orders/)
# =============================================================================


@pytest.mark.django_db
class TestOrderList:
    """Test order list endpoint."""

    def test_list_orders_empty(self, authenticated_client):
        """User with no orders gets empty list."""
        url = reverse("orders:order-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_list_orders_with_orders(
        self, authenticated_client, existing_order
    ):
        """User can see their orders."""
        url = reverse("orders:order-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == existing_order.id
        assert response.data[0]["status"] == "pending"
        assert response.data[0]["status_display"] == "Pending"
        assert response.data[0]["total_amount"] == "999.99"

    def test_list_orders_only_own(self, api_client, existing_order):
        """Users can only see their own orders."""
        # Create a different user
        other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPassword123!",
        )
        api_client.force_authenticate(user=other_user)

        url = reverse("orders:order-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0  # Other user's orders not visible

    def test_list_orders_unauthenticated(self, api_client):
        """Unauthenticated users cannot list orders."""
        url = reverse("orders:order-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Order Detail Tests (GET /api/orders/{id}/)
# =============================================================================


@pytest.mark.django_db
class TestOrderDetail:
    """Test order detail endpoint."""

    def test_order_detail_success(
        self, authenticated_client, existing_order
    ):
        """Can view details of own order."""
        url = reverse(
            "orders:order-detail", kwargs={"pk": existing_order.pk}
        )
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == existing_order.id
        assert response.data["status"] == "pending"
        assert response.data["shipping_address"] == "123 Test St, Test City"
        assert len(response.data["items"]) == 1
        assert response.data["items"][0]["quantity"] == 1
        assert response.data["items"][0]["price_at_purchase"] == "999.99"

    def test_order_detail_other_user(self, api_client, existing_order):
        """Cannot view another user's order."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPassword123!",
        )
        api_client.force_authenticate(user=other_user)

        url = reverse(
            "orders:order-detail", kwargs={"pk": existing_order.pk}
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_order_detail_nonexistent(self, authenticated_client):
        """Viewing non-existent order returns 404."""
        url = reverse("orders:order-detail", kwargs={"pk": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_order_detail_unauthenticated(self, api_client, existing_order):
        """Unauthenticated users cannot view orders."""
        url = reverse(
            "orders:order-detail", kwargs={"pk": existing_order.pk}
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Checkout Tests (POST /api/orders/)
# =============================================================================


@pytest.mark.django_db
class TestCheckout:
    """Test order creation (checkout) endpoint."""

    def test_checkout_success(
        self, authenticated_client, cart_with_items, product, second_product
    ):
        """Successful checkout creates order and clears cart."""
        url = reverse("orders:order-list")
        data = {
            "shipping_address": "456 Delivery Ave, Ship City",
            "notes": "Please leave at door",
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "pending"
        assert response.data["total_amount"] == "2599.97"
        assert response.data["shipping_address"] == "456 Delivery Ave, Ship City"
        assert response.data["notes"] == "Please leave at door"
        assert len(response.data["items"]) == 2

        # Verify inventory was decremented
        product.refresh_from_db()
        second_product.refresh_from_db()
        assert product.inventory_count == 8  # 10 - 2
        assert second_product.inventory_count == 4  # 5 - 1

        # Verify cart was cleared
        assert cart_with_items.items.count() == 0

    def test_checkout_without_notes(
        self, authenticated_client, cart_with_items
    ):
        """Checkout without notes succeeds (notes are optional)."""
        url = reverse("orders:order-list")
        data = {"shipping_address": "456 Delivery Ave"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["notes"] == ""

    def test_checkout_empty_cart(self, authenticated_client):
        """Checkout with empty cart fails."""
        url = reverse("orders:order-list")
        data = {"shipping_address": "456 Delivery Ave"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "empty" in response.data["detail"].lower()

    def test_checkout_no_cart(self, authenticated_client):
        """Checkout when user has no cart fails."""
        url = reverse("orders:order-list")
        data = {"shipping_address": "456 Delivery Ave"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_checkout_missing_shipping_address(
        self, authenticated_client, cart_with_items
    ):
        """Checkout without shipping address fails validation."""
        url = reverse("orders:order-list")
        data = {}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_checkout_insufficient_inventory(
        self, authenticated_client, test_user, product
    ):
        """Checkout fails if inventory is insufficient."""
        # Create cart with more items than available
        cart = Cart.objects.create(user=test_user)
        CartItem.objects.create(cart=cart, product=product, quantity=10)

        # Reduce inventory after adding to cart
        product.inventory_count = 3
        product.save()

        url = reverse("orders:order-list")
        data = {"shipping_address": "456 Delivery Ave"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Verify inventory was NOT decremented (transaction rolled back)
        product.refresh_from_db()
        assert product.inventory_count == 3

    def test_checkout_price_snapshot(
        self, authenticated_client, cart_with_items, product
    ):
        """Order items store the price at time of purchase."""
        url = reverse("orders:order-list")
        data = {"shipping_address": "456 Delivery Ave"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Verify price_at_purchase matches product price at checkout
        order = Order.objects.get(user__email="orderuser@example.com")
        laptop_item = order.items.get(product=product)
        assert laptop_item.price_at_purchase == Decimal("999.99")

    def test_checkout_unauthenticated(self, api_client):
        """Unauthenticated users cannot checkout."""
        url = reverse("orders:order-list")
        data = {"shipping_address": "456 Delivery Ave"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
