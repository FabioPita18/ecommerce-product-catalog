"""
Product and Category Models for the E-Commerce Catalog.

This module defines the core data models for product management:
- Category: Product categories for organizing the catalog
- Product: Individual products for sale

Design Decisions:
- Categories use a flat structure (no nesting) for simplicity
- Products use slug fields for SEO-friendly URLs
- Soft delete via is_active flag (never hard delete products with orders)
- Timestamps for auditing (created_at, updated_at)

Django Model docs: https://docs.djangoproject.com/en/5.0/topics/db/models/

Relationships:
- Category -> Product (One-to-Many via ForeignKey)
- Product -> CartItem (reverse relation via 'cart_items')
- Product -> OrderItem (reverse relation via 'order_items')
"""

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """
    Product Category for organizing products.

    Categories are used to group related products together for easier browsing.
    Examples: Electronics, Clothing, Books, Home & Garden

    URL Pattern: /api/categories/electronics/ (using slug)

    Fields:
        name: Display name for the category (unique)
        slug: URL-friendly identifier, auto-generated from name if not provided
        description: Optional description for category pages
        image: Optional thumbnail image for visual representation
        is_active: Controls visibility in the storefront (soft delete pattern)
        created_at: Timestamp when category was created
        updated_at: Timestamp when category was last modified

    Design Notes:
        - Using flat structure (no parent/child) for MVP simplicity
        - Slug is unique to ensure clean URLs
        - is_active allows hiding categories without deleting them
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category display name (must be unique)"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly identifier (auto-generated from name if not provided)"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional category description for category pages"
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        help_text="Category thumbnail image"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Inactive categories are hidden from the store"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self) -> str:
        """Return category name for display in admin and shell."""
        return self.name

    def save(self, *args, **kwargs):
        """
        Auto-generate slug from name if not provided.

        This ensures every category has a URL-friendly slug without
        requiring manual input. Uses Django's slugify() which:
        - Converts to lowercase
        - Replaces spaces with hyphens
        - Removes non-alphanumeric characters
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def product_count(self) -> int:
        """
        Return count of active products in this category.

        Used in admin list view and API responses to show category popularity.
        Only counts active products (not soft-deleted ones).
        """
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """
    Product model representing items for sale.

    This is the core model of the e-commerce platform. Products are linked
    to categories and can be added to carts and orders.

    Key Features:
        - Linked to Category (required via ForeignKey)
        - Price stored as Decimal for monetary accuracy (never use Float!)
        - Inventory tracking for stock management
        - Featured flag for homepage promotion
        - Soft delete via is_active flag

    Fields:
        name: Product display name
        slug: URL-friendly identifier for product pages
        description: Detailed product description (supports markdown)
        price: Product price as Decimal (max 10 digits, 2 decimal places)
        category: ForeignKey to Category (required)
        image: Main product image
        inventory_count: Number of items in stock
        is_active: Controls visibility (soft delete pattern)
        featured: Flag for homepage/special placement
        created_at: Timestamp when product was created
        updated_at: Timestamp when product was last modified

    Indexing Strategy:
        - slug: For URL lookups (unique constraint provides index)
        - is_active: Frequently filtered
        - featured + is_active: For homepage queries
        - category + is_active: For category listing pages
        - created_at: For "newest" sorting
        - price: For price range filtering

    Design Notes:
        - Using Decimal for price to avoid floating-point errors
        - inventory_count is PositiveIntegerField (can't go negative)
        - Slug auto-generated from name if not provided
        - Related names allow reverse lookups (category.products.all())
    """

    name = models.CharField(
        max_length=200,
        help_text="Product display name"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL-friendly identifier (must be unique)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed product description (supports markdown)"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in base currency (e.g., USD). Use Decimal for accuracy."
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Product category (required). Deleting category deletes products."
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        help_text="Main product image"
    )
    inventory_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of items in stock (cannot be negative)"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Inactive products are hidden from the store"
    )
    featured = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Featured products appear on the homepage"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            # Composite index for category listings (filtered by active status)
            models.Index(fields=['category', 'is_active']),
            # Composite index for homepage featured products
            models.Index(fields=['featured', 'is_active']),
            # Index for newest products sorting
            models.Index(fields=['-created_at']),
            # Index for price range filtering
            models.Index(fields=['price']),
        ]

    def __str__(self) -> str:
        """Return product name for display in admin and shell."""
        return self.name

    def save(self, *args, **kwargs):
        """
        Auto-generate slug from name if not provided.

        This ensures every product has a URL-friendly slug without
        requiring manual input. The slug must be unique, so if there's
        a collision, you'll get a database error - in a production app,
        you might want to append a suffix to handle duplicates.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self) -> bool:
        """
        Check if product has available inventory.

        Used in templates and API responses to show stock status.
        Returns True if inventory_count > 0.
        """
        return self.inventory_count > 0
