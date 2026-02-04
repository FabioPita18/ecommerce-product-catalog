"""
Product API Views using Django REST Framework.

This module will contain ViewSets for:
- ProductViewSet: CRUD operations for products + custom actions
- CategoryViewSet: List and retrieve categories

DRF ViewSets automatically generate URL patterns for standard actions:
- list:    GET    /api/products/
- create:  POST   /api/products/
- retrieve: GET   /api/products/{id}/
- update:  PUT    /api/products/{id}/
- partial_update: PATCH /api/products/{id}/
- destroy: DELETE /api/products/{id}/

Custom actions (via @action decorator):
- featured: GET /api/products/featured/
- search:   GET /api/products/search/?q=term

ViewSet docs: https://www.django-rest-framework.org/api-guide/viewsets/

Views will be implemented in Phase 3.
"""

# Views will be implemented in Phase 3
# Example structure:
#
# from rest_framework import viewsets
# from rest_framework.decorators import action
# from rest_framework.response import Response
#
# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.filter(is_active=True)
#     ...
