# Production Dockerfile for Django Backend
#
# Uses multi-stage build to minimize final image size:
# 1. Builder stage: Compiles Python wheels (handles C extensions)
# 2. Production stage: Copies pre-built wheels, runs as non-root user
#
# Multi-stage builds: https://docs.docker.com/build/building/multi-stage/

# Stage 1: Build Python wheels
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies needed for compiling C extensions (psycopg2, Pillow)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Install Python packages from pre-built wheels
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY --chown=appuser:appuser . .

# Collect static files for serving by WhiteNoise
RUN python manage.py collectstatic --noinput 2>/dev/null || true

USER appuser

# Railway injects PORT env var; default to 8000 for local Docker usage
EXPOSE ${PORT:-8000}

# Run with Gunicorn, binding to Railway's PORT (or 8000 if not set)
# Shell form is required for environment variable substitution
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 config.wsgi:application
