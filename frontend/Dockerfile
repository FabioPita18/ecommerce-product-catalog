# Production Dockerfile for React Frontend
#
# Uses multi-stage build:
# 1. Builder stage: Installs dependencies and builds the Vite production bundle
# 2. Production stage: Serves static files with Nginx
#
# The final image is tiny (~25MB) since it only contains Nginx and static HTML/JS/CSS.
#
# Railway-specific:
# - nginx:alpine has built-in envsubst support for /etc/nginx/templates/*.template
# - Railway auto-injects PORT; BACKEND_URL and BACKEND_HOST must be set manually

# Stage 1: Build the React application
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files first for better Docker layer caching
# (dependencies change less often than source code)
COPY package*.json ./
RUN npm ci

# Copy source code and build
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy the built static files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config template (contains ${PORT}, ${BACKEND_URL}, ${BACKEND_HOST} placeholders)
# nginx:alpine auto-substitutes env vars in /etc/nginx/templates/*.template at startup
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Remove the default nginx config to avoid conflicts
RUN rm -f /etc/nginx/conf.d/default.conf

# Default values for local Docker Compose usage (Railway overrides these)
ENV PORT=80
ENV BACKEND_URL=http://backend:8000
ENV BACKEND_HOST=backend

EXPOSE ${PORT}

# nginx:alpine's default entrypoint handles envsubst automatically
# for files in /etc/nginx/templates/ — no custom CMD needed
