"""
django-filter FilterSets for Products.

FilterSets enable query parameter filtering on API endpoints, e.g.:
    /api/products/?category=electronics
    /api/products/?min_price=10&max_price=100
    /api/products/?in_stock=true
    /api/products/?featured=true
    /api/products/?search=laptop

All filters are optional and can be combined freely.

django-filter docs: https://django-filter.readthedocs.io/
"""

import django_filters
from django.db.models import Q

from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Filter products by various criteria.

    Available filters:
        min_price: Minimum price (inclusive) - e.g., ?min_price=10
        max_price: Maximum price (inclusive) - e.g., ?max_price=100
        category: Category slug - e.g., ?category=electronics
        in_stock: Stock availability - e.g., ?in_stock=true
        featured: Featured status - e.g., ?featured=true
        search: Text search in name and description - e.g., ?search=laptop

    All filters are optional and combinable:
        /api/products/?category=electronics&min_price=100&in_stock=true
    """

    # Price range filters using lookup expressions
    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        help_text="Minimum price (inclusive)",
    )
    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        help_text="Maximum price (inclusive)",
    )

    # Filter by category slug (not ID) for SEO-friendly URLs
    category = django_filters.CharFilter(
        field_name="category__slug",
        help_text="Category slug (e.g., 'electronics')",
    )

    # Custom method filter for stock availability
    in_stock = django_filters.BooleanFilter(
        method="filter_in_stock",
        help_text="Filter by stock availability (true/false)",
    )

    # Direct boolean filter for featured products
    featured = django_filters.BooleanFilter(
        help_text="Filter featured products (true/false)",
    )

    # Custom method filter for text search
    search = django_filters.CharFilter(
        method="filter_search",
        help_text="Search in product name and description",
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "featured",
            "in_stock",
            "min_price",
            "max_price",
            "search",
        ]

    def filter_in_stock(self, queryset, name, value):
        """
        Filter by stock availability.

        ?in_stock=true  -> Only products with inventory > 0
        ?in_stock=false -> Only products with inventory = 0 (out of stock)

        Why a custom method instead of a simple BooleanFilter?
        Because 'in_stock' is a computed property, not a database field.
        We translate it to an inventory_count query.
        """
        if value is True:
            return queryset.filter(inventory_count__gt=0)
        elif value is False:
            return queryset.filter(inventory_count=0)
        return queryset

    def filter_search(self, queryset, name, value):
        """
        Full-text search across product name and description.

        Uses case-insensitive contains (icontains) for simple search.
        For production at scale, consider PostgreSQL full-text search
        or a dedicated search engine like Elasticsearch.

        The Q objects allow combining conditions with OR logic:
        a product matches if the search term is in the name OR description.
        """
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )
