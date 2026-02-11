"""
DRF ViewSets for Products and Categories.

ViewSets provide automatic URL routing for standard CRUD operations,
plus the ability to add custom actions via the @action decorator.

Permission Strategy:
    - Anyone (including unauthenticated users) can read products/categories
    - Only admin users can create, update, or delete products

ViewSet docs: https://www.django-rest-framework.org/api-guide/viewsets/
"""

from django.db import models
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .filters import ProductFilter
from .models import Category, Product
from .serializers import (
    CategoryDetailSerializer,
    CategorySerializer,
    ProductCreateUpdateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List all categories",
        description="Returns all active categories with product counts.",
    ),
    retrieve=extend_schema(
        summary="Get category details",
        description="Returns category details with its active products.",
    ),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Category operations (read-only).

    Endpoints:
        GET  /api/categories/           -> List all active categories
        GET  /api/categories/{slug}/    -> Category detail with products

    Categories are managed through Django Admin, not the API.
    ReadOnlyModelViewSet only provides list and retrieve actions.

    Why ReadOnlyModelViewSet?
        - Categories are managed by admins through Django Admin
        - No need for create/update/delete via API
        - Simpler and more secure than full ModelViewSet
    """

    queryset = Category.objects.filter(is_active=True)
    # Use slug instead of pk for URL lookups (/api/categories/electronics/)
    lookup_field = "slug"

    def get_serializer_class(self):
        """
        Use detailed serializer for retrieve action.

        The retrieve endpoint includes nested products, while the
        list endpoint keeps it lightweight with just category info.
        """
        if self.action == "retrieve":
            return CategoryDetailSerializer
        return CategorySerializer

    def get_queryset(self):
        """
        Annotate categories with product count for efficiency.

        Using Django's Count annotation instead of the model property
        avoids N+1 queries: one query for all categories + counts,
        instead of one query per category to count products.

        Note: We use 'annotated_product_count' instead of 'product_count'
        to avoid conflicting with the @property on the model.
        """
        return super().get_queryset().annotate(
            annotated_product_count=Count(
                "products",
                filter=models.Q(products__is_active=True),
            )
        )


@extend_schema_view(
    list=extend_schema(
        summary="List products",
        description=(
            "Returns paginated list of active products with filtering support."
        ),
        parameters=[
            OpenApiParameter(
                name="category", description="Filter by category slug"
            ),
            OpenApiParameter(
                name="min_price", description="Minimum price"
            ),
            OpenApiParameter(
                name="max_price", description="Maximum price"
            ),
            OpenApiParameter(
                name="in_stock", description="Filter by availability"
            ),
            OpenApiParameter(
                name="featured", description="Filter featured products"
            ),
            OpenApiParameter(
                name="search", description="Search in name/description"
            ),
            OpenApiParameter(
                name="ordering",
                description="Sort by: price, -price, name, -name, -created_at",
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Get product details",
        description="Returns full product information.",
    ),
    create=extend_schema(
        summary="Create product",
        description="Create a new product (admin only).",
    ),
    update=extend_schema(
        summary="Update product",
        description="Update product details (admin only).",
    ),
    partial_update=extend_schema(
        summary="Partial update product",
        description="Update specific product fields (admin only).",
    ),
    destroy=extend_schema(
        summary="Delete product",
        description="Delete a product (admin only).",
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations.

    Endpoints:
        GET    /api/products/              -> List (with filtering & pagination)
        GET    /api/products/{slug}/       -> Detail
        POST   /api/products/              -> Create (admin only)
        PUT    /api/products/{slug}/       -> Update (admin only)
        PATCH  /api/products/{slug}/       -> Partial update (admin only)
        DELETE /api/products/{slug}/       -> Delete (admin only)

    Custom Actions:
        GET /api/products/featured/        -> Featured products
        GET /api/products/search/?q=term   -> Search products
    """

    queryset = Product.objects.filter(is_active=True)
    lookup_field = "slug"

    # Filter backends: DjangoFilterBackend for custom filters, OrderingFilter for sorting
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductFilter

    # Fields that can be used for ordering via ?ordering=price or ?ordering=-price
    ordering_fields = ["price", "name", "created_at"]
    ordering = ["-created_at"]  # Default ordering: newest first

    def get_serializer_class(self):
        """
        Select serializer based on action.

        Different actions need different serializers:
        - list: Lightweight for performance
        - retrieve: Full details
        - create/update: Write serializer with validation
        """
        if self.action == "list":
            return ProductListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        """
        Set permissions based on action.

        Read operations (list, retrieve, featured, search) are public.
        Write operations (create, update, delete) require admin.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        """
        Optimize queryset with select_related.

        select_related('category') performs a SQL JOIN so that
        accessing product.category doesn't trigger an extra query.
        Without this, listing 12 products would be 13 queries (N+1 problem).
        """
        return super().get_queryset().select_related("category")

    @extend_schema(
        summary="Get featured products",
        description="Returns up to 8 featured products for homepage display.",
    )
    @action(detail=False, methods=["get"])
    def featured(self, request):
        """
        GET /api/products/featured/

        Returns featured products for homepage carousel/grid.
        Limited to 8 products for performance.
        Not paginated since it's a fixed small set.
        """
        products = self.get_queryset().filter(featured=True)[:8]
        serializer = ProductListSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Search products",
        description="Full-text search across product name and description.",
        parameters=[
            OpenApiParameter(
                name="q",
                description="Search query (minimum 2 characters)",
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        GET /api/products/search/?q=laptop

        Simple search endpoint that searches across name and description.
        For advanced search at scale, consider Elasticsearch.
        """
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response(
                {"error": "Search query is required. Use ?q=your+search+term"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(query) < 2:
            return Response(
                {"error": "Search query must be at least 2 characters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        products = self.get_queryset().filter(
            models.Q(name__icontains=query)
            | models.Q(description__icontains=query)
        )[:20]  # Limit results for performance

        serializer = ProductListSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data)
