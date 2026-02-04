"""
Product Filters using django-filter.

This module will contain FilterSet classes for the Product model.
FilterSets enable query parameter filtering like:
- /api/products/?category=1
- /api/products/?price_min=10&price_max=100
- /api/products/?in_stock=true

django-filter docs: https://django-filter.readthedocs.io/

Example (to be implemented in Phase 2):
    class ProductFilter(django_filters.FilterSet):
        price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
        price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

        class Meta:
            model = Product
            fields = ['category', 'is_active', 'featured']
"""
