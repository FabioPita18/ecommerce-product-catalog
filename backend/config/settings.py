"""
Django Settings for E-Commerce Product Catalog.

This settings file follows the 12-factor app methodology:
- All configuration is loaded from environment variables
- Secrets are never hardcoded
- Sensible defaults for development, strict settings for production

12-Factor App: https://12factor.net/
Django Settings Reference: https://docs.djangoproject.com/en/5.0/ref/settings/

Environment Variables:
    See .env.example for all required environment variables.
    Copy .env.example to .env and fill in your values.
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# =============================================================================
# Path Configuration
# =============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'
# BASE_DIR points to the 'backend' directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
# The .env file should be in the project root (parent of backend)
# load_dotenv() searches parent directories automatically
load_dotenv(BASE_DIR.parent / ".env")


# =============================================================================
# Core Django Settings
# =============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
# This key is used for cryptographic signing (sessions, tokens, etc.)
# Generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-default-key-change-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
# Debug mode exposes sensitive information in error pages
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# ALLOWED_HOSTS: List of host/domain names this site can serve
# Prevents HTTP Host header attacks
# Format in .env: ALLOWED_HOSTS=example.com,www.example.com
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")


# =============================================================================
# Application Definition
# =============================================================================

# Django's built-in apps
DJANGO_APPS = [
    "django.contrib.admin",  # Admin interface
    "django.contrib.auth",  # Authentication framework
    "django.contrib.contenttypes",  # Content type framework (for permissions)
    "django.contrib.sessions",  # Session framework
    "django.contrib.messages",  # Messaging framework
    "django.contrib.staticfiles",  # Static file handling
]

# Third-party packages
THIRD_PARTY_APPS = [
    "rest_framework",  # Django REST Framework
    "rest_framework_simplejwt",  # JWT authentication
    "rest_framework_simplejwt.token_blacklist",  # Token blacklisting for logout
    "corsheaders",  # CORS handling
    "django_filters",  # Filtering for DRF
    "drf_spectacular",  # OpenAPI schema generation
]

# Our custom apps
LOCAL_APPS = [
    "users",  # Custom user model and authentication
    "products",  # Product catalog
    "cart",  # Shopping cart
    "orders",  # Order management
]

# Combined list - order matters for some Django features
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# =============================================================================
# Middleware Configuration
# =============================================================================
# Middleware processes requests/responses in order (top to bottom for requests,
# bottom to top for responses)

MIDDLEWARE = [
    # Security middleware should be first
    "django.middleware.security.SecurityMiddleware",
    # CORS middleware must be before CommonMiddleware
    # Handles Cross-Origin Resource Sharing headers
    "corsheaders.middleware.CorsMiddleware",
    # Session middleware (required for admin)
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Common operations (URL normalization, etc.)
    "django.middleware.common.CommonMiddleware",
    # CSRF protection (required for forms)
    "django.middleware.csrf.CsrfViewMiddleware",
    # Authentication (adds request.user)
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Message framework (flash messages)
    "django.contrib.messages.middleware.MessageMiddleware",
    # Clickjacking protection
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =============================================================================
# URL Configuration
# =============================================================================

ROOT_URLCONF = "config.urls"


# =============================================================================
# Template Configuration
# =============================================================================
# Templates are used for Django admin and any server-rendered pages

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =============================================================================
# WSGI Configuration
# =============================================================================

WSGI_APPLICATION = "config.wsgi.application"


# =============================================================================
# Database Configuration
# =============================================================================
# Using PostgreSQL for production-grade features:
# - Full-text search, JSON fields, array fields
# - Better performance under concurrent load
# - ACID compliance
#
# DATABASE_URL format: postgresql://USER:PASSWORD@HOST:PORT/DATABASE
# Docs: https://docs.djangoproject.com/en/5.0/ref/databases/#postgresql-notes

# Parse DATABASE_URL into Django's DATABASES format
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ecommerce_user:ecommerce_password@localhost:5432/ecommerce_db",
)


def parse_database_url(url: str) -> dict:
    """
    Parse a DATABASE_URL into Django's database configuration format.

    Format: postgresql://USER:PASSWORD@HOST:PORT/DATABASE

    Why not use dj-database-url?
    - One less dependency
    - Simple URL format for our needs
    - Educational: shows what the package would do
    """
    # Remove the scheme
    url = url.replace("postgresql://", "").replace("postgres://", "")

    # Split user:password from host:port/database
    credentials, host_db = url.split("@")
    user, password = credentials.split(":")

    # Split host:port from database
    host_port, database = host_db.split("/")

    # Handle optional port
    if ":" in host_port:
        host, port = host_port.split(":")
    else:
        host = host_port
        port = "5432"

    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": database,
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": port,
    }


DATABASES = {"default": parse_database_url(DATABASE_URL)}


# =============================================================================
# Custom User Model
# =============================================================================
# IMPORTANT: This must be set BEFORE running migrations!
# Django's default User model uses username, but we want email-based auth.
# Docs: https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#specifying-a-custom-user-model

AUTH_USER_MODEL = "users.User"


# =============================================================================
# Password Validation
# =============================================================================
# Django's built-in password validators ensure password strength
# Docs: https://docs.djangoproject.com/en/5.0/topics/auth/passwords/

AUTH_PASSWORD_VALIDATORS = [
    {
        # Prevents password similar to user attributes (email, name)
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        # Enforces minimum length (default 8 characters)
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        # Prevents common passwords (uses a list of 20,000 common passwords)
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        # Prevents entirely numeric passwords
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =============================================================================
# Internationalization
# =============================================================================
# Docs: https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

# Use UTC for database storage, convert to user's timezone in frontend
TIME_ZONE = "UTC"

# Enable Django's translation system
USE_I18N = True

# Enable timezone-aware datetimes
USE_TZ = True


# =============================================================================
# Static Files (CSS, JavaScript, Images)
# =============================================================================
# Docs: https://docs.djangoproject.com/en/5.0/howto/static-files/

# URL prefix for static files
STATIC_URL = "static/"

# Directory where collectstatic will collect static files for production
STATIC_ROOT = BASE_DIR / "staticfiles"


# =============================================================================
# Media Files (User Uploads)
# =============================================================================
# Docs: https://docs.djangoproject.com/en/5.0/topics/files/

# URL prefix for media files
MEDIA_URL = os.getenv("MEDIA_URL", "/media/")

# Directory where uploaded files are stored
MEDIA_ROOT = BASE_DIR / os.getenv("MEDIA_ROOT", "media")


# =============================================================================
# Default Primary Key Type
# =============================================================================
# BigAutoField supports larger IDs than AutoField (up to 9 quintillion)
# Recommended for new projects in Django 3.2+

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =============================================================================
# Django REST Framework Configuration
# =============================================================================
# Docs: https://www.django-rest-framework.org/api-guide/settings/

REST_FRAMEWORK = {
    # Authentication: Use JWT for API authentication
    # JWTAuthentication reads the token from Authorization header
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Permissions: Allow read access to anyone, write access to authenticated users
    # This can be overridden per-view using permission_classes
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    # Pagination: Use page number pagination (e.g., ?page=2)
    # Returns: { "count": 100, "next": "...", "previous": "...", "results": [...] }
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,  # Products per page (good for 3x4 or 4x3 grids)
    # Filtering: Enable filtering, searching, and ordering
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",  # ?category=1
        "rest_framework.filters.SearchFilter",  # ?search=term
        "rest_framework.filters.OrderingFilter",  # ?ordering=-price
    ],
    # Schema: Use drf-spectacular for OpenAPI 3.0 schema generation
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Throttling: Rate limiting (optional, uncomment to enable)
    # "DEFAULT_THROTTLE_CLASSES": [
    #     "rest_framework.throttling.AnonRateThrottle",
    #     "rest_framework.throttling.UserRateThrottle",
    # ],
    # "DEFAULT_THROTTLE_RATES": {
    #     "anon": "100/hour",
    #     "user": "1000/hour",
    # },
}


# =============================================================================
# Simple JWT Configuration
# =============================================================================
# Docs: https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html

SIMPLE_JWT = {
    # Token Lifetimes
    # Access token: Short-lived, sent with every request
    # Refresh token: Long-lived, used to get new access tokens
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME", "60"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("REFRESH_TOKEN_LIFETIME", "1440"))  # 24 hours
    ),
    # Token Rotation: Issue new refresh token with each refresh
    # This invalidates the old refresh token for security
    "ROTATE_REFRESH_TOKENS": True,
    # Blacklisting: Add old refresh tokens to blacklist after rotation
    # Requires 'rest_framework_simplejwt.token_blacklist' in INSTALLED_APPS
    "BLACKLIST_AFTER_ROTATION": True,
    # Token Types: Accept only "Bearer" prefix in Authorization header
    # Usage: Authorization: Bearer <token>
    "AUTH_HEADER_TYPES": ("Bearer",),
    # Token Classes: Use AccessToken for authentication
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    # Signing Key: Use separate key for JWT signing
    # Falls back to SECRET_KEY if not set
    "SIGNING_KEY": os.getenv("JWT_SECRET_KEY", SECRET_KEY),
    # Algorithm: Use HS256 (HMAC with SHA-256)
    "ALGORITHM": "HS256",
}


# =============================================================================
# CORS Configuration
# =============================================================================
# CORS (Cross-Origin Resource Sharing) controls which domains can access the API
# Docs: https://github.com/adamchainz/django-cors-headers

# Allowed Origins: List of origins that can make cross-origin requests
# Origin = scheme + domain + port (e.g., http://localhost:5173)
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

# Allow credentials: Required for cookies/auth headers in cross-origin requests
CORS_ALLOW_CREDENTIALS = True

# Allowed Methods: HTTP methods allowed in cross-origin requests
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# Allowed Headers: HTTP headers allowed in cross-origin requests
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]


# =============================================================================
# DRF Spectacular (OpenAPI Documentation)
# =============================================================================
# Docs: https://drf-spectacular.readthedocs.io/en/latest/settings.html

SPECTACULAR_SETTINGS = {
    "TITLE": "E-Commerce Product Catalog API",
    "DESCRIPTION": """
    RESTful API for an e-commerce product catalog.

    ## Features
    - Product catalog with categories and filtering
    - Shopping cart management
    - Order processing and history
    - User authentication with JWT

    ## Authentication
    Most endpoints require authentication. Use the `/api/auth/login/` endpoint
    to obtain JWT tokens, then include the access token in the Authorization header:

    ```
    Authorization: Bearer <access_token>
    ```
    """,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # Organize endpoints by app/tag
    "TAGS": [
        {"name": "auth", "description": "Authentication endpoints"},
        {"name": "products", "description": "Product catalog endpoints"},
        {"name": "categories", "description": "Category endpoints"},
        {"name": "cart", "description": "Shopping cart endpoints"},
        {"name": "orders", "description": "Order management endpoints"},
    ],
}


# =============================================================================
# Security Settings
# =============================================================================
# These settings enhance security. Some are more strict in production.
# Docs: https://docs.djangoproject.com/en/5.0/topics/security/

if not DEBUG:
    # HTTPS Settings
    SECURE_SSL_REDIRECT = True  # Redirect HTTP to HTTPS
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Cookie Security
    SESSION_COOKIE_SECURE = True  # Only send session cookie over HTTPS
    CSRF_COOKIE_SECURE = True  # Only send CSRF cookie over HTTPS

    # HSTS (HTTP Strict Transport Security)
    # Tells browsers to only use HTTPS for this domain
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# X-Frame-Options: Prevent site from being embedded in iframes (clickjacking protection)
X_FRAME_OPTIONS = "DENY"

# X-Content-Type-Options: Prevent MIME type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True


# =============================================================================
# Logging Configuration
# =============================================================================
# Docs: https://docs.djangoproject.com/en/5.0/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
