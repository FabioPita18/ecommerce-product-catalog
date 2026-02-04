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

Models will be implemented in Phase 2.
"""

from django.db import models  # noqa: F401

# Models will be implemented in Phase 2:
# - Category
# - Product
#
# See CLAUDE.md in the backend directory for the model specifications.
