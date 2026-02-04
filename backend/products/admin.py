"""
Django Admin Configuration for Products App.

This module registers Product and Category models with Django admin.
Admin configuration provides a user-friendly interface for managing data.

Key Features:
- CategoryAdmin: List view with name, slug, product count, filtering
- ProductAdmin:
  - List view with name, price, category, stock status
  - Filters by category, is_active, featured
  - Search by name, description
  - Bulk actions for activate/deactivate
  - Inline editing for price, inventory, status flags

Django Admin docs: https://docs.djangoproject.com/en/5.0/ref/contrib/admin/

Design Notes:
- Using @admin.register decorator for cleaner registration
- prepopulated_fields for auto-slug generation in admin
- list_editable for quick inline editing of common fields
- format_html for safe HTML rendering in custom columns
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model.

    Features:
    - List display: name, slug, product count, active status, created date
    - Filters: active status, creation date
    - Search: name and description
    - Auto-slug generation from name
    - Collapsible timestamps section
    """

    # List view configuration
    list_display = ['name', 'slug', 'product_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']

    # Auto-populate slug from name when creating new category
    prepopulated_fields = {'slug': ('name',)}

    # Make timestamps read-only (auto-generated)
    readonly_fields = ['created_at', 'updated_at']

    # Organize fields into logical groups
    fieldsets = (
        # Main fields section (no title)
        (None, {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        # Status section
        ('Status', {
            'fields': ('is_active',)
        }),
        # Timestamps section (collapsed by default to reduce clutter)
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Automatically managed timestamps'
        }),
    )

    def product_count(self, obj):
        """
        Display count of active products in this category.

        Uses the model's product_count property which filters by is_active.
        This gives admins a quick view of category popularity.
        """
        return obj.product_count

    # Set column header for custom method
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for Product model.

    Features:
    - List display: name, category, price, inventory, stock status, flags
    - Filters: category, active status, featured, creation date
    - Search: name and description
    - Auto-slug generation from name
    - Inline editing for price, inventory, is_active, featured
    - Color-coded stock status display

    The list_editable feature allows quick updates without opening each product.
    This is useful for inventory management and bulk price updates.
    """

    # List view configuration
    # Fields shown in the table view
    list_display = [
        'name',
        'category',
        'price',
        'inventory_count',
        'is_in_stock_display',
        'is_active',
        'featured',
        'created_at'
    ]

    # Sidebar filters for narrowing down the list
    list_filter = ['category', 'is_active', 'featured', 'created_at']

    # Fields searchable via the search box
    search_fields = ['name', 'description']

    # Auto-populate slug from name when creating new product
    prepopulated_fields = {'slug': ('name',)}

    # Make timestamps read-only (auto-generated)
    readonly_fields = ['created_at', 'updated_at']

    # Fields that can be edited directly in the list view
    # This enables quick updates without opening individual records
    list_editable = ['price', 'inventory_count', 'is_active', 'featured']

    # Number of items per page (reduce for performance with large datasets)
    list_per_page = 25

    # Organize fields into logical groups for the detail/edit view
    fieldsets = (
        # Main product information
        (None, {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        # Pricing and inventory section
        ('Pricing & Inventory', {
            'fields': ('price', 'inventory_count'),
            'description': 'Set product price and stock levels'
        }),
        # Media section
        ('Media', {
            'fields': ('image',),
            'description': 'Product images'
        }),
        # Status flags section
        ('Status', {
            'fields': ('is_active', 'featured'),
            'description': 'Control product visibility and promotion'
        }),
        # Timestamps section (collapsed by default)
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Automatically managed timestamps'
        }),
    )

    # Custom admin actions for bulk operations
    actions = ['make_active', 'make_inactive', 'make_featured', 'remove_featured']

    def is_in_stock_display(self, obj):
        """
        Display stock status with color coding.

        Green checkmark for in-stock items, red X for out-of-stock.
        Uses format_html for safe HTML rendering (prevents XSS).
        """
        if obj.is_in_stock:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ In Stock</span>'
            )
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">✗ Out of Stock</span>'
        )

    # Set column header for custom method
    is_in_stock_display.short_description = 'Stock Status'

    # Admin actions for bulk operations
    @admin.action(description='Mark selected products as active')
    def make_active(self, request, queryset):
        """Bulk activate selected products."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} product(s) marked as active.')

    @admin.action(description='Mark selected products as inactive')
    def make_inactive(self, request, queryset):
        """Bulk deactivate selected products."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} product(s) marked as inactive.')

    @admin.action(description='Mark selected products as featured')
    def make_featured(self, request, queryset):
        """Bulk mark products as featured."""
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} product(s) marked as featured.')

    @admin.action(description='Remove featured status from selected products')
    def remove_featured(self, request, queryset):
        """Bulk remove featured status from products."""
        updated = queryset.update(featured=False)
        self.message_user(request, f'{updated} product(s) removed from featured.')
