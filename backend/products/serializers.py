"""
Product Serializers for Django REST Framework.

Serializers handle:
1. Converting model instances to JSON (serialization)
2. Converting JSON to model instances (deserialization)
3. Input validation

DRF Serializers docs: https://www.django-rest-framework.org/api-guide/serializers/

This module will contain:
- CategorySerializer: For category CRUD operations
- ProductListSerializer: Lightweight serializer for list views
- ProductDetailSerializer: Full serializer for detail views
- ProductCreateSerializer: For creating/updating products

Design Patterns Used:
- Separate read/write serializers for different use cases
- Nested serializers for related objects in read operations
- PrimaryKeyRelatedField for write operations (accepts ID instead of nested object)

Example (to be implemented in Phase 3):
    class ProductListSerializer(serializers.ModelSerializer):
        category = CategorySerializer(read_only=True)

        class Meta:
            model = Product
            fields = ['id', 'name', 'slug', 'price', 'category', 'image']
"""
