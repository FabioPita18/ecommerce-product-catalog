"""
Tests for Products API.

Test Structure:
    - TestCategoryAPI: Category endpoint tests
    - TestProductAPI: Product endpoint tests
    - TestProductFiltering: Filter and search tests
    - TestProductOrdering: Ordering tests

Testing Strategy:
    - Use pytest fixtures for test data setup
    - Test both success and error cases
    - Test permission boundaries (public read, admin write)
    - Test filtering, search, and ordering behavior

pytest-django docs: https://pytest-django.readthedocs.io/
"""

from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from products.models import Category, Product


# =============================================================================
# Fixtures - Reusable test data
# =============================================================================


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name="Electronics",
        slug="electronics",
        description="Electronic devices and accessories",
        is_active=True,
    )


@pytest.fixture
def second_category(db):
    """Create a second test category for filtering tests."""
    return Category.objects.create(
        name="Books",
        slug="books",
        description="Fiction and non-fiction books",
        is_active=True,
    )


@pytest.fixture
def product(db, category):
    """Create a test product."""
    return Product.objects.create(
        name="Test Laptop",
        slug="test-laptop",
        description="A powerful laptop for testing",
        price=Decimal("999.99"),
        category=category,
        inventory_count=10,
        is_active=True,
        featured=True,
    )


@pytest.fixture
def inactive_product(db, category):
    """Create an inactive product (should be hidden from API)."""
    return Product.objects.create(
        name="Inactive Product",
        slug="inactive-product",
        description="This product is not active",
        price=Decimal("99.99"),
        category=category,
        inventory_count=5,
        is_active=False,
    )


@pytest.fixture
def out_of_stock_product(db, category):
    """Create an out-of-stock product."""
    return Product.objects.create(
        name="Out of Stock Item",
        slug="out-of-stock-item",
        description="This item has no inventory",
        price=Decimal("49.99"),
        category=category,
        inventory_count=0,
        is_active=True,
    )


# =============================================================================
# Category API Tests
# =============================================================================


@pytest.mark.django_db
class TestCategoryAPI:
    """Tests for Category endpoints."""

    def test_list_categories(self, api_client, category):
        """GET /api/categories/ returns active categories."""
        url = reverse("category-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Categories endpoint is not paginated by default for ReadOnlyModelViewSet
        # but may be depending on pagination settings
        data = response.data
        # Handle both paginated and non-paginated responses
        results = data["results"] if isinstance(data, dict) and "results" in data else data
        assert len(results) >= 1
        assert results[0]["name"] == "Electronics"

    def test_category_detail(self, api_client, category, product):
        """GET /api/categories/{slug}/ returns category with products."""
        url = reverse("category-detail", args=[category.slug])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Electronics"
        assert "products" in response.data
        assert len(response.data["products"]) >= 1

    def test_category_detail_excludes_inactive_products(
        self, api_client, category, product, inactive_product
    ):
        """Category detail only shows active products."""
        url = reverse("category-detail", args=[category.slug])
        response = api_client.get(url)

        slugs = [p["slug"] for p in response.data["products"]]
        assert "test-laptop" in slugs
        assert "inactive-product" not in slugs

    def test_inactive_category_not_listed(self, api_client, db):
        """Inactive categories are not returned in list."""
        Category.objects.create(
            name="Hidden Category",
            slug="hidden",
            is_active=False,
        )
        url = reverse("category-list")
        response = api_client.get(url)

        data = response.data
        results = data["results"] if isinstance(data, dict) and "results" in data else data
        slugs = [c["slug"] for c in results]
        assert "hidden" not in slugs

    def test_category_has_product_count(self, api_client, category, product):
        """Categories include product_count field."""
        url = reverse("category-list")
        response = api_client.get(url)

        data = response.data
        results = data["results"] if isinstance(data, dict) and "results" in data else data
        electronics = next(c for c in results if c["slug"] == "electronics")
        assert electronics["product_count"] == 1


# =============================================================================
# Product API Tests
# =============================================================================


@pytest.mark.django_db
class TestProductAPI:
    """Tests for Product endpoints."""

    def test_list_products(self, api_client, product):
        """GET /api/products/ returns active products with pagination."""
        url = reverse("product-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Product list is paginated
        assert "count" in response.data
        assert "results" in response.data
        assert response.data["count"] >= 1

    def test_product_detail(self, api_client, product):
        """GET /api/products/{slug}/ returns full product details."""
        url = reverse("product-detail", args=[product.slug])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Laptop"
        assert response.data["is_in_stock"] is True
        assert "description" in response.data
        assert "inventory_count" in response.data

    def test_inactive_product_not_listed(self, api_client, inactive_product):
        """Inactive products are not shown in the list."""
        url = reverse("product-list")
        response = api_client.get(url)

        slugs = [p["slug"] for p in response.data["results"]]
        assert "inactive-product" not in slugs

    def test_inactive_product_not_retrievable(self, api_client, inactive_product):
        """Inactive products cannot be retrieved by slug."""
        url = reverse("product-detail", args=[inactive_product.slug])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_featured_products(self, api_client, product):
        """GET /api/products/featured/ returns featured products."""
        url = reverse("product-featured")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert any(p["slug"] == "test-laptop" for p in response.data)

    def test_product_includes_category(self, api_client, product):
        """Product response includes nested category data."""
        url = reverse("product-detail", args=[product.slug])
        response = api_client.get(url)

        assert "category" in response.data
        assert response.data["category"]["slug"] == "electronics"


# =============================================================================
# Product Filtering Tests
# =============================================================================


@pytest.mark.django_db
class TestProductFiltering:
    """Tests for product filtering and search."""

    def test_filter_by_category(self, api_client, product, category):
        """Filter products by category slug."""
        url = reverse("product-list")
        response = api_client.get(url, {"category": "electronics"})

        assert response.status_code == status.HTTP_200_OK
        for p in response.data["results"]:
            assert p["category"]["slug"] == "electronics"

    def test_filter_by_price_range(self, api_client, product):
        """Filter products by min and max price."""
        url = reverse("product-list")
        response = api_client.get(url, {"min_price": 500, "max_price": 1500})

        assert response.status_code == status.HTTP_200_OK
        for p in response.data["results"]:
            assert 500 <= float(p["price"]) <= 1500

    def test_filter_in_stock(self, api_client, product, out_of_stock_product):
        """Filter products by stock availability."""
        url = reverse("product-list")
        response = api_client.get(url, {"in_stock": "true"})

        assert response.status_code == status.HTTP_200_OK
        for p in response.data["results"]:
            assert p["is_in_stock"] is True

    def test_filter_out_of_stock(self, api_client, product, out_of_stock_product):
        """Filter to show only out-of-stock products."""
        url = reverse("product-list")
        response = api_client.get(url, {"in_stock": "false"})

        assert response.status_code == status.HTTP_200_OK
        for p in response.data["results"]:
            assert p["is_in_stock"] is False

    def test_filter_featured(self, api_client, product, out_of_stock_product):
        """Filter featured products."""
        url = reverse("product-list")
        response = api_client.get(url, {"featured": "true"})

        assert response.status_code == status.HTTP_200_OK
        for p in response.data["results"]:
            assert p["featured"] is True

    def test_search_products(self, api_client, product):
        """Search products by name via the search endpoint."""
        url = reverse("product-search")
        response = api_client.get(url, {"q": "laptop"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(p["slug"] == "test-laptop" for p in response.data)

    def test_search_by_description(self, api_client, product):
        """Search also matches product description."""
        url = reverse("product-search")
        response = api_client.get(url, {"q": "powerful"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_search_requires_query(self, api_client):
        """Search endpoint requires a query parameter."""
        url = reverse("product-search")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_minimum_length(self, api_client):
        """Search query must be at least 2 characters."""
        url = reverse("product-search")
        response = api_client.get(url, {"q": "a"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_combined_filters(self, api_client, product, category):
        """Multiple filters can be combined."""
        url = reverse("product-list")
        response = api_client.get(
            url,
            {
                "category": "electronics",
                "min_price": 500,
                "in_stock": "true",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        for p in response.data["results"]:
            assert p["category"]["slug"] == "electronics"
            assert float(p["price"]) >= 500
            assert p["is_in_stock"] is True


# =============================================================================
# Product Ordering Tests
# =============================================================================


@pytest.mark.django_db
class TestProductOrdering:
    """Tests for product ordering/sorting."""

    def test_order_by_price_ascending(self, api_client, product, category):
        """Order products by price (lowest first)."""
        Product.objects.create(
            name="Cheap Item",
            slug="cheap-item",
            price=Decimal("9.99"),
            category=category,
            inventory_count=5,
            is_active=True,
        )

        url = reverse("product-list")
        response = api_client.get(url, {"ordering": "price"})

        prices = [float(p["price"]) for p in response.data["results"]]
        assert prices == sorted(prices)

    def test_order_by_price_descending(self, api_client, product, category):
        """Order products by price (highest first)."""
        Product.objects.create(
            name="Expensive Item",
            slug="expensive-item",
            price=Decimal("9999.99"),
            category=category,
            inventory_count=3,
            is_active=True,
        )

        url = reverse("product-list")
        response = api_client.get(url, {"ordering": "-price"})

        prices = [float(p["price"]) for p in response.data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_order_by_name(self, api_client, product, category):
        """Order products alphabetically by name."""
        Product.objects.create(
            name="Alpha Product",
            slug="alpha-product",
            price=Decimal("29.99"),
            category=category,
            inventory_count=5,
            is_active=True,
        )

        url = reverse("product-list")
        response = api_client.get(url, {"ordering": "name"})

        names = [p["name"] for p in response.data["results"]]
        assert names == sorted(names)

    def test_default_ordering_newest_first(self, api_client, product, category):
        """Default ordering is newest first (-created_at)."""
        newer_product = Product.objects.create(
            name="Newer Product",
            slug="newer-product",
            price=Decimal("29.99"),
            category=category,
            inventory_count=5,
            is_active=True,
        )

        url = reverse("product-list")
        response = api_client.get(url)

        # The newest product should appear first
        assert response.data["results"][0]["slug"] == newer_product.slug
