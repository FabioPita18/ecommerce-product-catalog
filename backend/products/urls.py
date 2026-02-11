"""
URL Configuration for Products API.

Uses DRF's DefaultRouter for automatic URL generation from ViewSets.
The router inspects the ViewSet and creates URL patterns for all standard
actions (list, create, retrieve, update, partial_update, destroy) plus
any custom @action endpoints.

Generated URLs:
    /api/products/              -> ProductViewSet (list, create)
    /api/products/{slug}/       -> ProductViewSet (retrieve, update, destroy)
    /api/products/featured/     -> ProductViewSet.featured()
    /api/products/search/       -> ProductViewSet.search()
    /api/categories/            -> CategoryViewSet (list)
    /api/categories/{slug}/     -> CategoryViewSet (retrieve)

Note: These URLs are included in config/urls.py under the /api/ prefix.

DRF Routers docs: https://www.django-rest-framework.org/api-guide/routers/
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet

# DefaultRouter creates URL patterns automatically from ViewSets.
# It also provides an API root view that lists all endpoints.
router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
]
