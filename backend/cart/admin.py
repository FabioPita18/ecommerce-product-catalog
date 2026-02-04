"""
Django Admin Configuration for Cart App.

This module registers Cart and CartItem models with Django admin.
The cart admin provides visibility into user shopping carts for support purposes.

Key Features:
- CartAdmin: Show user, item count, total value, timestamps
- CartItemInline: Inline editor for cart items within cart view
- Read-only computed fields (totals, subtotals)
- raw_id_fields for efficient product lookup in large catalogs

Django Admin docs: https://docs.djangoproject.com/en/5.0/ref/contrib/admin/

Design Notes:
- Cart items displayed inline within cart admin for complete view
- Using raw_id_fields for product to avoid loading all products in dropdown
- Computed properties (totals) are read-only
- Admin is primarily for viewing/support, not for manual cart manipulation
"""

from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """
    Inline editor for cart items within the Cart admin view.

    TabularInline displays items in a compact table format, which is
    ideal for cart items where you want to see multiple items at once.

    Features:
    - Display product, quantity, subtotal in table rows
    - raw_id_fields for product to avoid loading all products
    - Read-only subtotal (computed from price × quantity)
    - No extra blank rows (extra=0)

    Design Notes:
    - raw_id_fields is essential for performance with large product catalogs
    - subtotal is computed dynamically, so it's read-only
    - added_at shows when item was added to cart
    """

    model = CartItem

    # Number of empty forms to display for adding new items
    # Set to 0 since cart manipulation is typically done via API
    extra = 0

    # Fields that are computed/auto-generated and shouldn't be edited
    readonly_fields = ['subtotal_display', 'added_at']

    # Use raw_id_fields for ForeignKey to avoid loading all products
    # This shows a lookup widget instead of a dropdown
    raw_id_fields = ['product']

    # Fields to display in the inline table
    fields = ['product', 'quantity', 'subtotal_display', 'added_at']

    def subtotal_display(self, obj):
        """
        Display item subtotal formatted as currency.

        Uses the model's subtotal property which calculates quantity × price.
        """
        if obj.pk:
            return f"${obj.subtotal:.2f}"
        return "-"

    subtotal_display.short_description = 'Subtotal'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin interface for Cart model.

    Provides a view into user shopping carts for customer support.
    Carts are displayed with their items inline for a complete view.

    Features:
    - List display: user, item count, total amount, last updated
    - Search by user email
    - Read-only computed fields (totals)
    - Inline cart items for complete visibility

    Design Notes:
    - This admin is primarily for viewing, not manual manipulation
    - Cart operations should typically be done via API
    - Useful for customer support to see cart contents
    """

    # List view configuration
    list_display = ['user', 'total_items_display', 'total_amount_display', 'updated_at']

    # Enable search by user email for customer support
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

    # Fields that are computed/auto-generated
    readonly_fields = ['created_at', 'updated_at', 'total_items_display', 'total_amount_display']

    # Include inline cart items in the detail view
    inlines = [CartItemInline]

    # List view filters
    list_filter = ['created_at', 'updated_at']

    # Organize fields in the detail view
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Cart Summary', {
            'fields': ('total_items_display', 'total_amount_display'),
            'description': 'Computed values based on cart contents'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_items_display(self, obj):
        """
        Display total items count.

        Uses the model's total_items property which sums all quantities.
        """
        return obj.total_items

    total_items_display.short_description = 'Total Items'

    def total_amount_display(self, obj):
        """
        Display total cart value formatted as currency.

        Uses the model's total_amount property which sums all subtotals.
        """
        return f"${obj.total_amount:.2f}"

    total_amount_display.short_description = 'Total Amount'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Standalone admin for CartItem (optional, mainly for debugging).

    While cart items are typically managed through the Cart inline,
    this provides direct access for debugging or data management.

    Features:
    - List display: cart owner, product, quantity, subtotal
    - Filter by cart user
    - Search by product name or user email
    """

    list_display = ['cart_user', 'product', 'quantity', 'subtotal_display', 'added_at']
    list_filter = ['added_at']
    search_fields = ['cart__user__email', 'product__name']
    raw_id_fields = ['cart', 'product']
    readonly_fields = ['subtotal_display', 'added_at', 'updated_at']

    def cart_user(self, obj):
        """Display the cart owner's email."""
        return obj.cart.user.email

    cart_user.short_description = 'User'

    def subtotal_display(self, obj):
        """Display item subtotal formatted as currency."""
        return f"${obj.subtotal:.2f}"

    subtotal_display.short_description = 'Subtotal'
