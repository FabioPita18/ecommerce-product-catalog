"""
Root URL Configuration for E-Commerce Product Catalog API.

This module defines the top-level URL routing for the entire application.

URL Structure:
    /admin/                 - Django admin interface
    /api/products/          - Product catalog endpoints
    /api/categories/        - Category endpoints (part of products app)
    /api/cart/              - Shopping cart endpoints
    /api/orders/            - Order management endpoints
    /api/auth/              - Authentication endpoints (register, login, etc.)
    /api/health/            - Health check endpoint
    /api/docs/              - Swagger UI documentation
    /api/redoc/             - ReDoc documentation
    /api/schema/            - OpenAPI schema (JSON/YAML)

Media Files:
    In development, Django serves uploaded media files.
    In production, use a web server (nginx) or CDN.

Django URL docs: https://docs.djangoproject.com/en/5.0/topics/http/urls/
DRF Router docs: https://www.django-rest-framework.org/api-guide/routers/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import RedirectView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.

    Returns a simple JSON response indicating the service is running.
    Used by:
    - Docker health checks
    - Kubernetes liveness probes
    - Load balancer health checks
    - Monitoring systems

    Response:
        {
            "status": "healthy",
            "service": "ecommerce-api"
        }
    """
    return JsonResponse(
        {
            "status": "healthy",
            "service": "ecommerce-api",
        }
    )


# =============================================================================
# URL Patterns
# =============================================================================

urlpatterns = [
    # -------------------------------------------------------------------------
    # Root Redirect
    # -------------------------------------------------------------------------
    # Redirect the bare domain to /api/ so visitors see something useful
    path("", RedirectView.as_view(url="/api/", permanent=False)),
    # -------------------------------------------------------------------------
    # Admin Interface
    # -------------------------------------------------------------------------
    # Django's built-in admin interface for managing data
    # Accessible at /admin/ (requires superuser account)
    path("admin/", admin.site.urls),
    # -------------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------------
    # Simple endpoint to verify the service is running
    # No authentication required
    path("api/health/", health_check, name="health-check"),
    # -------------------------------------------------------------------------
    # API Documentation (drf-spectacular)
    # -------------------------------------------------------------------------
    # OpenAPI schema in JSON/YAML format (for tools and clients)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI - Interactive API documentation
    # Try out endpoints directly in the browser
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # ReDoc - Alternative documentation UI (read-only, better for reference)
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # -------------------------------------------------------------------------
    # API Endpoints (App URLs)
    # -------------------------------------------------------------------------
    # Each app defines its own URL patterns which are included here
    # with an appropriate prefix
    # Products App: /api/products/, /api/categories/
    path("api/", include("products.urls")),
    # Cart App: /api/cart/
    path("api/cart/", include("cart.urls")),
    # Orders App: /api/orders/
    path("api/orders/", include("orders.urls")),
    # Users App: /api/auth/
    path("api/auth/", include("users.urls")),
]


# =============================================================================
# Media Files (Development Only)
# =============================================================================
# In development, Django serves uploaded files directly.
# In production, configure your web server (nginx, Apache) or use cloud storage.
#
# Why only in development?
# - Django's static/media serving is not optimized for production
# - No caching, no CDN, single-threaded
# - Production should use nginx, AWS S3, or similar

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# =============================================================================
# Admin Site Configuration
# =============================================================================
# Customize the admin site header and title

admin.site.site_header = "E-Commerce Admin"
admin.site.site_title = "E-Commerce Product Catalog"
admin.site.index_title = "Welcome to E-Commerce Admin"
