"""
DRF Serializers for Products and Categories.

Serializers handle converting between Python objects and JSON, plus input validation.

Serializer Hierarchy:
    - CategorySerializer: Basic category data for nested views
    - CategoryDetailSerializer: Category with nested products (for detail endpoint)
    - ProductListSerializer: Minimal data for list views (performance)
    - ProductDetailSerializer: Full data for detail views
    - ProductCreateUpdateSerializer: For POST/PUT operations (admin only)

Design Principles:
    - Never use fields = '__all__' (explicit is better, prevents accidental exposure)
    - Separate read and write serializers when needed
    - Use SerializerMethodField for computed properties
    - Validate business rules in serializers

DRF Serializers docs: https://www.django-rest-framework.org/api-guide/serializers/
"""

from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """
    Basic Category serializer for nested views.

    Used when category data is embedded in product responses.
    Keeps response size small by only including essential fields.

    Example response:
        {
            "id": 1,
            "name": "Electronics",
            "slug": "electronics",
            "description": "Smartphones, laptops, tablets, and accessories",
            "image": null,
            "product_count": 5
        }
    """

    # Use SerializerMethodField to handle both the annotated value
    # (from CategoryViewSet.get_queryset) and the model property fallback
    # (when used as a nested serializer in product responses).
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "product_count",
        ]

    def get_product_count(self, obj):
        """
        Return the product count, preferring the annotation for efficiency.

        When accessed via CategoryViewSet, the queryset has an
        'annotated_product_count' annotation (single query with COUNT).
        When used as a nested serializer, falls back to the model property
        (which does a separate COUNT query per category).
        """
        return getattr(obj, "annotated_product_count", obj.product_count)


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight Product serializer for list views.

    Used for: GET /api/products/
    Optimized for performance when listing many products - only includes
    the fields needed for product cards in the frontend.

    Why a separate list serializer?
        - List views return many products, so smaller payloads = faster
        - Detail fields like full description aren't needed in grid views
        - Nested category data is included for display without extra requests
    """

    category = CategorySerializer(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "category",
            "image",
            "is_in_stock",
            "featured",
        ]


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed Category serializer with nested products.

    Used for: GET /api/categories/{slug}/
    Includes a list of active products in the category so the frontend
    can display a category page with products in a single request.
    """

    products = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "product_count",
            "products",
            "created_at",
        ]

    def get_product_count(self, obj):
        """Return product count, preferring annotation over property."""
        return getattr(obj, "annotated_product_count", obj.product_count)

    def get_products(self, obj):
        """
        Return active products in this category.

        Limited to 12 products to keep response size reasonable.
        The frontend can paginate via the products endpoint for more.
        """
        products = obj.products.filter(is_active=True)[:12]
        return ProductListSerializer(
            products, many=True, context=self.context
        ).data


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Full Product serializer for detail views.

    Used for: GET /api/products/{slug}/
    Includes all product information for the product detail page.
    """

    category = CategorySerializer(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "category",
            "image",
            "inventory_count",
            "is_in_stock",
            "is_active",
            "featured",
            "created_at",
            "updated_at",
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating products.

    Used for: POST/PUT/PATCH /api/products/ (admin only)
    Accepts category_id instead of nested object for write operations.
    Includes business rule validation.

    Why a separate write serializer?
        - Read serializers nest related objects (category as JSON object)
        - Write operations accept IDs instead (category_id as integer)
        - Validation rules are only needed for writes
    """

    # Accept category by ID for writes, but only allow active categories
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source="category",
        write_only=True,
        help_text="ID of the category (must be an active category)",
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "description",
            "price",
            "category_id",
            "image",
            "inventory_count",
            "is_active",
            "featured",
        ]

    def validate_price(self, value):
        """Ensure price is positive. Prices of zero or negative make no sense."""
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )
        return value

    def validate_inventory_count(self, value):
        """Ensure inventory is non-negative. Can't have negative stock."""
        if value < 0:
            raise serializers.ValidationError(
                "Inventory count cannot be negative."
            )
        return value

    def validate_name(self, value):
        """Ensure product name is not too short for meaningful display."""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Product name must be at least 3 characters."
            )
        return value.strip()
