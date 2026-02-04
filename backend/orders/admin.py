"""
Django Admin Configuration for Orders App.

This module registers Order and OrderItem models with Django admin.
The orders admin is critical for order management and fulfillment.

Key Features:
- OrderAdmin: List with status badges, user, total, date
- OrderItemInline: View order items within order detail
- Color-coded status badges for visual status tracking
- Actions for status transitions (mark shipped, mark delivered)
- date_hierarchy for easy navigation by date
- Read-only price fields (immutable after order creation)

Django Admin docs: https://docs.djangoproject.com/en/5.0/ref/contrib/admin/

Design Notes:
- Orders are mostly read-only after creation (only status changes)
- Status is the main editable field for order management
- Price fields are read-only to maintain purchase history integrity
- Color-coded status badges provide quick visual status identification
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    Inline display for order items within Order admin view.

    Order items are read-only since orders are immutable after creation.
    Shows product, quantity, price at purchase, and subtotal.

    Features:
    - Compact table display of order items
    - All fields read-only (order history is immutable)
    - Subtotal computed from price_at_purchase × quantity
    - raw_id_fields for product lookup

    Design Notes:
    - extra=0 since orders can't have items added after creation
    - All fields are effectively read-only
    - Shows historical price (price_at_purchase), not current price
    """

    model = OrderItem

    # No extra blank rows (orders are immutable)
    extra = 0

    # Fields that should not be edited
    readonly_fields = ['product', 'quantity', 'price_at_purchase', 'subtotal_display']

    # Use raw_id_fields for product reference
    raw_id_fields = ['product']

    # Fields to display
    fields = ['product', 'quantity', 'price_at_purchase', 'subtotal_display']

    # Prevent adding/deleting items (orders are immutable)
    can_delete = False

    def has_add_permission(self, request, obj=None):
        """Prevent adding items to existing orders."""
        return False

    def subtotal_display(self, obj):
        """
        Display item subtotal formatted as currency.

        Uses price_at_purchase (historical price), not current product price.
        """
        if obj.pk:
            return f"${obj.subtotal:.2f}"
        return "-"

    subtotal_display.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for Order model.

    Provides order management capabilities for fulfillment workflow.
    Orders can have their status changed but are otherwise immutable.

    Features:
    - List display: order ID, user, status badge, items, total, date
    - Filter by status, creation date
    - Search by user email, shipping address
    - Color-coded status badges
    - Actions for bulk status updates
    - date_hierarchy for date-based navigation

    Order Workflow:
    - pending: New order, awaiting processing
    - processing: Being prepared for shipment
    - shipped: Sent to customer
    - delivered: Received by customer
    - cancelled: Order was cancelled

    Design Notes:
    - Only status field should be editable after creation
    - total_amount is stored at checkout, not computed
    - date_hierarchy enables quick date navigation in admin
    """

    # List view configuration
    list_display = [
        'id',
        'user',
        'status_badge',
        'item_count_display',
        'total_amount_display',
        'created_at'
    ]

    # Sidebar filters
    list_filter = ['status', 'created_at']

    # Search configuration
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'shipping_address']

    # Fields that cannot be edited (order history is immutable)
    readonly_fields = ['created_at', 'updated_at', 'total_amount', 'item_count_display']

    # Include inline order items
    inlines = [OrderItemInline]

    # Items per page
    list_per_page = 25

    # Enable date-based navigation (shows year/month/day links)
    date_hierarchy = 'created_at'

    # Organize fields in detail view
    fieldsets = (
        ('Customer', {
            'fields': ('user',),
            'description': 'Customer who placed this order'
        }),
        ('Order Details', {
            'fields': ('status', 'total_amount', 'item_count_display', 'notes'),
            'description': 'Order status and totals'
        }),
        ('Shipping', {
            'fields': ('shipping_address',),
            'description': 'Delivery information'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Custom admin actions for status management
    actions = [
        'mark_processing',
        'mark_shipped',
        'mark_delivered',
        'mark_cancelled'
    ]

    def status_badge(self, obj):
        """
        Display status with color-coded badge.

        Color scheme:
        - pending: Yellow (warning)
        - processing: Cyan (info)
        - shipped: Blue (primary)
        - delivered: Green (success)
        - cancelled: Red (danger)

        Uses format_html for safe HTML rendering.
        """
        colors = {
            'pending': '#FFC107',      # Warning yellow
            'processing': '#17A2B8',   # Info cyan
            'shipped': '#007BFF',      # Primary blue
            'delivered': '#28A745',    # Success green
            'cancelled': '#DC3545',    # Danger red
        }
        color = colors.get(obj.status, '#6C757D')  # Default gray

        return format_html(
            '<span style="'
            'background-color: {}; '
            'color: white; '
            'padding: 4px 12px; '
            'border-radius: 4px; '
            'font-size: 11px; '
            'font-weight: bold; '
            'text-transform: uppercase;'
            '">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'  # Enable sorting by status

    def item_count_display(self, obj):
        """Display total number of items in order."""
        return obj.item_count

    item_count_display.short_description = 'Items'

    def total_amount_display(self, obj):
        """Display order total formatted as currency."""
        return f"${obj.total_amount:.2f}"

    total_amount_display.short_description = 'Total'

    # Admin actions for order status management
    @admin.action(description='Mark selected orders as Processing')
    def mark_processing(self, request, queryset):
        """Bulk update orders to processing status."""
        # Only update orders that are currently pending
        updated = queryset.filter(status=Order.Status.PENDING).update(
            status=Order.Status.PROCESSING
        )
        self.message_user(request, f'{updated} order(s) marked as processing.')

    @admin.action(description='Mark selected orders as Shipped')
    def mark_shipped(self, request, queryset):
        """Bulk update orders to shipped status."""
        # Only update orders that are currently processing
        updated = queryset.filter(status=Order.Status.PROCESSING).update(
            status=Order.Status.SHIPPED
        )
        self.message_user(request, f'{updated} order(s) marked as shipped.')

    @admin.action(description='Mark selected orders as Delivered')
    def mark_delivered(self, request, queryset):
        """Bulk update orders to delivered status."""
        # Only update orders that are currently shipped
        updated = queryset.filter(status=Order.Status.SHIPPED).update(
            status=Order.Status.DELIVERED
        )
        self.message_user(request, f'{updated} order(s) marked as delivered.')

    @admin.action(description='Mark selected orders as Cancelled')
    def mark_cancelled(self, request, queryset):
        """Bulk cancel orders."""
        # Only cancel orders that are pending or processing
        cancellable = queryset.filter(
            status__in=[Order.Status.PENDING, Order.Status.PROCESSING]
        )
        updated = cancellable.update(status=Order.Status.CANCELLED)
        self.message_user(request, f'{updated} order(s) cancelled.')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Standalone admin for OrderItem (for debugging/reporting).

    While order items are typically viewed through Order inline,
    this provides direct access for data analysis or debugging.

    All fields are read-only since orders are immutable.
    """

    list_display = ['order', 'product', 'quantity', 'price_at_purchase', 'subtotal_display']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__user__email', 'product__name']
    raw_id_fields = ['order', 'product']

    # All fields are read-only (orders are immutable)
    readonly_fields = ['order', 'product', 'quantity', 'price_at_purchase']

    def subtotal_display(self, obj):
        """Display item subtotal formatted as currency."""
        return f"${obj.subtotal:.2f}"

    subtotal_display.short_description = 'Subtotal'

    def has_add_permission(self, request):
        """Prevent creating order items directly."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent editing order items."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting order items."""
        return False
