"""
Django Admin Configuration for Products App.

This module registers Product and Category models with Django admin.
Admin configuration provides a user-friendly interface for managing data.

Key Features to implement (Phase 2):
- CategoryAdmin: List view with name, slug, product count
- ProductAdmin:
  - List view with image thumbnail, name, price, category, stock
  - Filters by category, is_active, featured
  - Search by name, description
  - Actions for bulk activate/deactivate

Django Admin docs: https://docs.djangoproject.com/en/5.0/ref/contrib/admin/
"""

from django.contrib import admin  # noqa: F401

# Admin classes will be implemented in Phase 2
# Example structure:
#
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['name', 'category', 'price', 'inventory_count', 'is_active']
#     list_filter = ['category', 'is_active', 'featured']
#     search_fields = ['name', 'description']
#     prepopulated_fields = {'slug': ('name',)}
