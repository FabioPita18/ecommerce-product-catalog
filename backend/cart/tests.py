"""
Tests for Cart API.

Comprehensive tests for:
    - View cart (GET /api/cart/)
    - Clear cart (DELETE /api/cart/)
    - Cart summary (GET /api/cart/summary/)
    - Add item to cart (POST /api/cart/items/)
    - Update item quantity (PATCH /api/cart/items/{id}/)
    - Remove item from cart (DELETE /api/cart/items/{id}/)

Testing Strategy:
    - All cart endpoints require authentication (test 401 for anonymous)
    - Test cart auto-creation (lazy get_or_create)
    - Test inventory validation when adding/updating items
    - Test duplicate product handling (quantity increase vs new item)
    - Test cart total calculations
    - Use pytest fixtures for test data setup

pytest-django docs: https://pytest-django.readthedocs.io/
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cart.models import Cart, CartItem
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
    """Create a test user for cart tests."""
    return User.objects.create_user(
        email="cartuser@example.com",
        password="TestPassword123!",
        first_name="Cart",
        last_name="User",
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """
    Return an authenticated API client.

    Uses force_authenticate for simplicity in tests - avoids
    needing to go through the full JWT login flow for every test.
    """
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
def product_out_of_stock(db, category):
    """Create a product with zero inventory."""
    return Product.objects.create(
        name="Out of Stock Phone",
        slug="out-of-stock-phone",
        description="This phone is out of stock",
        price="499.99",
        category=category,
        inventory_count=0,
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
    """Create a cart with two items for testing."""
    cart = Cart.objects.create(user=test_user)
    item1 = CartItem.objects.create(cart=cart, product=product, quantity=2)
    item2 = CartItem.objects.create(
        cart=cart, product=second_product, quantity=1
    )
    return cart, item1, item2


# =============================================================================
# Cart View Tests (GET /api/cart/, DELETE /api/cart/)
# =============================================================================


@pytest.mark.django_db
class TestCartView:
    """Test cart view and clear endpoints."""

    def test_get_cart_empty(self, authenticated_client):
        """GET /api/cart/ returns empty cart for new user."""
        url = reverse("cart:cart")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["items"] == []
        assert response.data["total_items"] == 0
        assert response.data["total_amount"] == "0.00"

    def test_get_cart_with_items(self, authenticated_client, cart_with_items):
        """GET /api/cart/ returns cart with items and correct totals."""
        url = reverse("cart:cart")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["items"]) == 2
        assert response.data["total_items"] == 3  # 2 + 1
        # Total: 999.99 * 2 + 599.99 * 1 = 2599.97
        assert response.data["total_amount"] == "2599.97"

    def test_clear_cart(self, authenticated_client, cart_with_items):
        """DELETE /api/cart/ removes all items from cart."""
        url = reverse("cart:cart")
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify cart is empty
        cart = cart_with_items[0]
        assert cart.items.count() == 0

    def test_get_cart_unauthenticated(self, api_client):
        """Unauthenticated users cannot access cart."""
        url = reverse("cart:cart")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Cart Summary Tests (GET /api/cart/summary/)
# =============================================================================


@pytest.mark.django_db
class TestCartSummary:
    """Test lightweight cart summary endpoint."""

    def test_summary_empty_cart(self, authenticated_client):
        """Summary for user with no cart returns zeros."""
        url = reverse("cart:cart-summary")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_items"] == 0
        assert response.data["total_amount"] == "0.00"

    def test_summary_with_items(self, authenticated_client, cart_with_items):
        """Summary reflects correct count and total."""
        url = reverse("cart:cart-summary")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_items"] == 3
        assert response.data["total_amount"] == "2599.97"

    def test_summary_unauthenticated(self, api_client):
        """Unauthenticated users cannot access cart summary."""
        url = reverse("cart:cart-summary")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Add to Cart Tests (POST /api/cart/items/)
# =============================================================================


@pytest.mark.django_db
class TestAddToCart:
    """Test adding items to cart."""

    def test_add_item_success(self, authenticated_client, product):
        """Adding a valid product creates a cart item."""
        url = reverse("cart:cart-items")
        data = {"product_id": product.id, "quantity": 2}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantity"] == 2
        assert response.data["product"]["id"] == product.id

    def test_add_item_default_quantity(self, authenticated_client, product):
        """Adding without quantity defaults to 1."""
        url = reverse("cart:cart-items")
        data = {"product_id": product.id}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantity"] == 1

    def test_add_duplicate_increases_quantity(
        self, authenticated_client, product
    ):
        """Adding a product already in cart increases its quantity."""
        url = reverse("cart:cart-items")
        data = {"product_id": product.id, "quantity": 2}

        # Add first time
        response1 = authenticated_client.post(url, data, format="json")
        assert response1.status_code == status.HTTP_201_CREATED

        # Add same product again
        response2 = authenticated_client.post(url, data, format="json")
        assert response2.status_code == status.HTTP_200_OK
        assert response2.data["quantity"] == 4  # 2 + 2

    def test_add_out_of_stock_product(
        self, authenticated_client, product_out_of_stock
    ):
        """Cannot add out-of-stock product to cart."""
        url = reverse("cart:cart-items")
        data = {"product_id": product_out_of_stock.id, "quantity": 1}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_exceeding_inventory(self, authenticated_client, product):
        """Cannot add more than available inventory."""
        url = reverse("cart:cart-items")
        data = {"product_id": product.id, "quantity": 100}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_nonexistent_product(self, authenticated_client):
        """Cannot add product that doesn't exist."""
        url = reverse("cart:cart-items")
        data = {"product_id": 99999, "quantity": 1}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_item_unauthenticated(self, api_client, product):
        """Unauthenticated users cannot add to cart."""
        url = reverse("cart:cart-items")
        data = {"product_id": product.id, "quantity": 1}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Update Cart Item Tests (PATCH /api/cart/items/{id}/)
# =============================================================================


@pytest.mark.django_db
class TestUpdateCartItem:
    """Test updating cart item quantity."""

    def test_update_quantity_success(
        self, authenticated_client, cart_with_items
    ):
        """Can update quantity of existing cart item."""
        cart, item1, item2 = cart_with_items
        url = reverse("cart:cart-item-detail", kwargs={"pk": item1.pk})
        data = {"quantity": 5}

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["quantity"] == 5

    def test_update_exceeding_inventory(
        self, authenticated_client, cart_with_items
    ):
        """Cannot update quantity beyond available inventory."""
        cart, item1, item2 = cart_with_items
        url = reverse("cart:cart-item-detail", kwargs={"pk": item1.pk})
        data = {"quantity": 100}

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_nonexistent_item(self, authenticated_client):
        """Updating non-existent cart item returns 404."""
        url = reverse("cart:cart-item-detail", kwargs={"pk": 99999})
        data = {"quantity": 1}

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_other_users_item(
        self, api_client, cart_with_items
    ):
        """Cannot update another user's cart item."""
        cart, item1, item2 = cart_with_items
        # Create a different user and authenticate
        other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPassword123!",
        )
        api_client.force_authenticate(user=other_user)

        url = reverse("cart:cart-item-detail", kwargs={"pk": item1.pk})
        data = {"quantity": 5}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# Remove Cart Item Tests (DELETE /api/cart/items/{id}/)
# =============================================================================


@pytest.mark.django_db
class TestRemoveCartItem:
    """Test removing items from cart."""

    def test_remove_item_success(
        self, authenticated_client, cart_with_items
    ):
        """Can remove an item from cart."""
        cart, item1, item2 = cart_with_items
        url = reverse("cart:cart-item-detail", kwargs={"pk": item1.pk})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert cart.items.count() == 1  # One item remaining

    def test_remove_nonexistent_item(self, authenticated_client):
        """Removing non-existent cart item returns 404."""
        url = reverse("cart:cart-item-detail", kwargs={"pk": 99999})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_unauthenticated(self, api_client, cart_with_items):
        """Unauthenticated users cannot remove cart items."""
        cart, item1, item2 = cart_with_items
        url = reverse("cart:cart-item-detail", kwargs={"pk": item1.pk})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
