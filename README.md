# E-Commerce Product Catalog

> Full-stack e-commerce application with product browsing, shopping cart, and order management

[![Django](https://img.shields.io/badge/Django-5.0-092E20?logo=django)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![MUI](https://img.shields.io/badge/MUI-7-007FFF?logo=mui)](https://mui.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/tests-83_passing-success)](.github/workflows/ci.yml)

## Overview

A modern e-commerce platform featuring product catalog browsing, advanced search and filtering, shopping cart management, and complete order processing. Built with Django REST Framework and React as a portfolio project demonstrating full-stack development skills.

### Key Features

- **Product Catalog** - Browse 15 products across 5 categories with images
- **Search & Filtering** - Filter by category, price range, stock status; sort by price/name/date
- **Shopping Cart** - Add/remove items, update quantities, inventory validation
- **User Authentication** - JWT-based register/login/logout with token refresh
- **Order Management** - Checkout from cart, order history, order cancellation
- **Responsive Design** - Mobile-first UI with Material-UI components
- **Admin Panel** - Django admin for managing products, orders, and users

### Intentionally Excluded

- Payment processing (Stripe/PayPal) - separate project scope
- Email notifications - future enhancement
- Product reviews/ratings - future enhancement

## Tech Stack

### Backend

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Runtime |
| Django | 5.0.1 | Web framework |
| Django REST Framework | 3.14.0 | REST API |
| PostgreSQL | 15 | Database |
| Simple JWT | 5.3.1 | JWT authentication |
| django-filter | 23.5 | API filtering |
| drf-spectacular | 0.27.0 | OpenAPI documentation |
| Gunicorn | 21.2.0 | Production WSGI server |
| pytest-django | 4.7.0 | Testing |

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| React | 19 | UI framework |
| TypeScript | 5.9 | Type safety |
| Vite | 7 | Build tool |
| Material-UI (MUI) | 7 | Component library |
| React Router | 7 | Client-side routing |
| TanStack Query | 5 | Server state management |
| React Hook Form | 7 | Form handling |
| Zod | 4 | Schema validation |
| Axios | 1.6 | HTTP client |

### Infrastructure

| Technology | Purpose |
|---|---|
| Docker & Docker Compose | Containerization |
| GitHub Actions | CI/CD pipeline |
| Nginx | Production reverse proxy |

## API Endpoints

### Products
```
GET    /api/products/              List products (paginated, filtered)
GET    /api/products/{slug}/       Product detail
GET    /api/products/featured/     Featured products
GET    /api/products/search/       Search products (?q=term)
```

### Categories
```
GET    /api/categories/            List all categories
GET    /api/categories/{slug}/     Category detail with products
```

### Cart
```
GET    /api/cart/                  Get user's cart
GET    /api/cart/summary/          Cart item count and total
POST   /api/cart/items/            Add item to cart
PUT    /api/cart/items/{id}/       Update cart item quantity
DELETE /api/cart/items/{id}/       Remove item from cart
DELETE /api/cart/clear/            Clear entire cart
```

### Orders
```
GET    /api/orders/                List user's orders
GET    /api/orders/{id}/           Order detail
POST   /api/orders/                Create order (checkout)
POST   /api/orders/{id}/cancel/    Cancel a pending order
```

### Authentication
```
POST   /api/auth/register/         User registration
POST   /api/auth/login/            Login (returns JWT tokens)
POST   /api/auth/logout/           Logout (blacklist refresh token)
POST   /api/auth/refresh/          Refresh access token
GET    /api/auth/profile/          Get user profile
PUT    /api/auth/profile/          Update user profile
POST   /api/auth/password/change/  Change password
```

### Other
```
GET    /api/health/                Health check
GET    /api/docs/                  Swagger UI documentation
GET    /api/redoc/                 ReDoc documentation
```

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 22+
- PostgreSQL 15+ (or Docker)

### Option 1: Docker (Recommended)

```bash
# Clone and start all services
git clone https://github.com/yourusername/ecommerce-product-catalog.git
cd ecommerce-product-catalog

# Start PostgreSQL and Django backend
docker compose up -d

# Run database migrations
docker compose exec backend python manage.py migrate

# Load sample data (5 categories, 15 products)
docker compose exec backend python manage.py loaddata fixtures/categories.json
docker compose exec backend python manage.py loaddata fixtures/products.json

# Create admin account
docker compose exec backend python manage.py createsuperuser

# Start the frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env with your PostgreSQL credentials

# Set up database
python manage.py migrate
python manage.py loaddata fixtures/categories.json
python manage.py loaddata fixtures/products.json
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Access Points

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/ |
| Admin Panel | http://localhost:8000/admin/ |
| API Docs (Swagger) | http://localhost:8000/api/docs/ |
| API Docs (ReDoc) | http://localhost:8000/api/redoc/ |

> **Note:** When running the backend via Docker Compose, the default port is 8002. Update `frontend/vite.config.ts` proxy target accordingly.

## Running Tests

### Backend (83 tests)
```bash
cd backend
source venv/bin/activate
pytest -v                          # Run all tests
pytest -v --cov=. --cov-report=html  # With coverage report
pytest -k "test_product"           # Run specific tests
```

Test breakdown:
- Products: 25 tests (CRUD, filtering, search, ordering)
- Users: 21 tests (registration, login, logout, profile, password)
- Cart: 21 tests (add, update, remove, clear, inventory validation)
- Orders: 16 tests (checkout, detail, list, permissions)

### Frontend
```bash
cd frontend
npm run build      # TypeScript check + production build
npm run lint       # ESLint
npx tsc -b         # Type check only
```

## Environment Variables

### Backend (.env)
```bash
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_db
JWT_SECRET_KEY=your-jwt-secret
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

## Project Structure

```
ecommerce-product-catalog/
├── .github/workflows/
│   └── ci.yml                     # CI/CD pipeline
├── backend/
│   ├── config/                    # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── products/                  # Product catalog app
│   │   ├── models.py              # Product, Category models
│   │   ├── serializers.py         # List, detail, create serializers
│   │   ├── views.py               # ViewSets with search/featured actions
│   │   ├── filters.py             # Price, category, stock filters
│   │   ├── admin.py               # Admin with inline editors
│   │   ├── urls.py
│   │   └── tests.py               # 25 tests
│   ├── users/                     # Authentication app
│   │   ├── models.py              # Custom User (email-based)
│   │   ├── serializers.py
│   │   ├── views.py               # Register, login, profile, password
│   │   ├── urls.py
│   │   └── tests.py               # 21 tests
│   ├── cart/                      # Shopping cart app
│   │   ├── models.py              # Cart, CartItem models
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py               # 21 tests
│   ├── orders/                    # Order management app
│   │   ├── models.py              # Order, OrderItem models
│   │   ├── serializers.py
│   │   ├── views.py               # List, detail, checkout, cancel
│   │   ├── urls.py
│   │   └── tests.py               # 16 tests
│   ├── fixtures/                  # Sample data
│   │   ├── categories.json        # 5 categories
│   │   └── products.json          # 15 products
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   ├── Dockerfile.prod
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── components/common/     # Shared components
│   │   │   ├── Navbar.tsx         # Nav bar with cart badge & user menu
│   │   │   ├── ProductCard.tsx    # Product card with add-to-cart
│   │   │   └── ProtectedRoute.tsx # Auth-guarded route wrapper
│   │   ├── pages/                 # Route pages
│   │   │   ├── HomePage.tsx       # Featured products grid
│   │   │   ├── ProductsPage.tsx   # Filterable product listing
│   │   │   ├── ProductDetailPage.tsx
│   │   │   ├── LoginPage.tsx      # Login with form validation
│   │   │   ├── RegisterPage.tsx   # Registration with validation
│   │   │   ├── CartPage.tsx       # Cart management
│   │   │   ├── CheckoutPage.tsx   # Address form + order placement
│   │   │   ├── OrdersPage.tsx     # Order history
│   │   │   └── OrderDetailPage.tsx # Order detail with cancel
│   │   ├── services/              # API service layer
│   │   │   ├── api.ts             # Axios instance + JWT interceptors
│   │   │   ├── auth.ts            # Auth API calls
│   │   │   ├── products.ts        # Product/category API calls
│   │   │   ├── cart.ts            # Cart API calls
│   │   │   └── orders.ts          # Order API calls
│   │   ├── hooks/                 # TanStack Query hooks
│   │   │   ├── useAuth.ts         # Auth context consumer
│   │   │   ├── useProducts.ts     # Product query hooks
│   │   │   ├── useCart.ts         # Cart query/mutation hooks
│   │   │   └── useOrders.ts       # Order query/mutation hooks
│   │   ├── contexts/              # React Context
│   │   │   ├── AuthContext.tsx     # Auth provider (login/logout/register)
│   │   │   └── authContextDef.ts  # Context type + creation
│   │   ├── types/index.ts         # TypeScript type definitions
│   │   ├── theme/index.ts         # MUI theme customization
│   │   ├── utils/productImages.ts # Placeholder product images
│   │   ├── App.tsx                # Root component + routing
│   │   └── main.tsx               # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── Dockerfile.prod
│   └── nginx.conf                 # Production Nginx config
├── docker-compose.yml             # Development environment
├── docker-compose.prod.yml        # Production environment
├── .env.example
└── README.md
```

## Database Schema

```
┌──────────────┐       ┌──────────────────┐       ┌────────────────┐
│   Category   │       │     Product      │       │      User      │
├──────────────┤       ├──────────────────┤       ├────────────────┤
│ id           │◄──────│ category_id      │       │ id             │
│ name         │       │ name             │       │ email (PK)     │
│ slug         │       │ slug             │       │ first_name     │
│ description  │       │ description      │       │ last_name      │
│ is_active    │       │ price            │       │ password       │
└──────────────┘       │ image            │       └───────┬────────┘
                       │ inventory_count  │               │
                       │ is_active        │               │
                       │ featured         │       ┌───────┴────────┐
                       └────────┬─────────┘       │      Cart      │
                                │                 ├────────────────┤
                       ┌────────┴─────────┐       │ user_id (1:1)  │
                       │    CartItem      │       └───────┬────────┘
                       ├──────────────────┤               │
                       │ cart_id          │◄──────────────┘
                       │ product_id       │
                       │ quantity         │
                       └──────────────────┘

┌──────────────────┐       ┌──────────────────┐
│      Order       │       │    OrderItem     │
├──────────────────┤       ├──────────────────┤
│ user_id          │       │ order_id         │
│ status           │◄──────│ product_id       │
│ total_amount     │       │ quantity         │
│ shipping_address │       │ price_at_purchase│
│ notes            │       └──────────────────┘
└──────────────────┘

Order Status: pending ──→ processing ──→ shipped ──→ delivered
                 └─────→ cancelled
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push to `main`/`develop` and on pull requests:

1. **Backend Tests** - Python + pytest with PostgreSQL service container
2. **Frontend Checks** - TypeScript compilation, ESLint, production build
3. **Docker Build** - Build production images (main branch only)

## Production Deployment

```bash
# Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Load data
docker compose -f docker-compose.prod.yml exec backend python manage.py loaddata fixtures/categories.json
docker compose -f docker-compose.prod.yml exec backend python manage.py loaddata fixtures/products.json
```

The production setup uses:
- **Backend**: Gunicorn with 4 workers behind Nginx
- **Frontend**: Vite production build served by Nginx with gzip and cache headers
- **Nginx**: Serves static files, proxies `/api` requests to Django

## License

This project is licensed under the MIT License.

## Acknowledgments

- Built with [Django](https://www.djangoproject.com/) and [React](https://react.dev/)
- UI components from [Material-UI](https://mui.com/)
- Product placeholder images from [Unsplash](https://unsplash.com/)
