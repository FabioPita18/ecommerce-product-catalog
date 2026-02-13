# =============================================================================
# Dockerfile for E-Commerce Product Catalog Backend
# =============================================================================
# Multi-stage build for optimized production images.
#
# Build stages:
# 1. builder: Install dependencies with build tools
# 2. production: Slim runtime image with only what's needed
#
# Build: docker build -t ecommerce-backend .
# Run: docker run -p 8000:8000 ecommerce-backend
#
# Docker best practices applied:
# - Multi-stage builds for smaller images
# - Non-root user for security
# - Layer caching optimization
# - Health checks included
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder
# -----------------------------------------------------------------------------
# Install dependencies with all build tools available.
# This stage is discarded in the final image.

FROM python:3.12-slim as builder

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from creating .pyc files
# PYTHONUNBUFFERED: Ensures Python output is sent straight to terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required for building Python packages
# - gcc, libpq-dev: Required for psycopg2 (PostgreSQL adapter)
# - libjpeg-dev, zlib1g-dev: Required for Pillow (image processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and use virtual environment
# This allows us to copy just the venv to the production stage
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# -----------------------------------------------------------------------------
# Stage 2: Production
# -----------------------------------------------------------------------------
# Slim image with only runtime dependencies.

FROM python:3.12-slim as production

# Labels for image metadata
LABEL maintainer="E-Commerce Team" \
      version="1.0" \
      description="E-Commerce Product Catalog API"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Use the virtual environment from builder stage
    PATH="/opt/venv/bin:$PATH" \
    # Django settings
    DJANGO_SETTINGS_MODULE=config.settings

# Install runtime dependencies only (no build tools)
# - libpq5: PostgreSQL client library (runtime only, not -dev)
# - libjpeg62-turbo: JPEG library (runtime only)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
# Running as root in containers is a security risk
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
# .dockerignore should exclude venv, __pycache__, etc.
COPY --chown=appuser:appgroup . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R appuser:appgroup /app/staticfiles /app/media

# Switch to non-root user
USER appuser

# Expose port 8000 (Django default)
EXPOSE 8000

# Health check
# Verifies the service is responding to requests
# --fail: Exit with error if HTTP request fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health/')" || exit 1

# Default command: Run Gunicorn production server
# --bind: Listen on all interfaces, port 8000
# --workers: Number of worker processes (2-4 × CPU cores recommended)
# --access-logfile: Log requests to stdout
# --error-logfile: Log errors to stderr
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "config.wsgi:application"]
