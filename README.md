# E-Commerce Product Catalog

> Full-stack e-commerce application with shopping cart, product management, and order processing

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://ecommerce-catalog.vercel.app)
[![Django](https://img.shields.io/badge/Django-5.0-092E20?logo=django)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Material-UI](https://img.shields.io/badge/MUI-5.15-007FFF?logo=mui)](https://mui.com/)
[![Tests](https://img.shields.io/badge/tests-passing-success)](https://github.com/yourusername/ecommerce-product-catalog/actions)
[![Coverage](https://img.shields.io/badge/coverage-75%25-brightgreen)](https://github.com/yourusername/ecommerce-product-catalog)

## 📋 Overview

A modern, production-ready e-commerce platform featuring product catalog browsing, advanced search and filtering, shopping cart functionality, and complete order management. Built with Django and React, it demonstrates best practices in full-stack development, database design, and user experience.

## 🎯 Problem Statement

Small to medium businesses need an affordable, customizable e-commerce solution that:
- Displays products attractively with categories and filtering
- Provides a seamless shopping cart experience
- Handles user authentication and order history
- Offers easy product management through an admin panel
- Works flawlessly on mobile and desktop devices

## ✨ Solution

A complete e-commerce platform featuring:
- **Product Catalog**: Browse products by category with advanced filtering
- **Smart Search**: Full-text search with autocomplete suggestions
- **Shopping Cart**: Add/remove items, update quantities, persist across sessions
- **User Accounts**: Registration, login, profile management, order history
- **Order Processing**: Complete checkout flow (no payment integration in MVP)
- **Admin Panel**: Django admin for easy product and order management
- **Responsive Design**: Mobile-first approach with Material-UI components

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.0.1 + Django REST Framework
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Search**: PostgreSQL full-text search
- **Image Handling**: Pillow
- **Testing**: pytest-django
- **Deployment**: Railway

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI) v5
- **Routing**: React Router v6
- **State Management**: React Context API + TanStack Query
- **Forms**: React Hook Form
- **HTTP Client**: Axios
- **Deployment**: Vercel

### DevOps
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest (backend), Jest + RTL (frontend)
- **Code Quality**: ESLint, Prettier, Black, mypy

## 🚀 Key Features

### Current (MVP)
- [x] Product catalog with categories and subcategories
- [x] Product listing (grid and list views)
- [x] Product detail pages with image galleries
- [x] Advanced search (by title, description, category)
- [x] Filtering (price range, category, availability)
- [x] Sorting (price, name, newest)
- [x] Shopping cart (add/remove, update quantities)
- [x] Cart persistence (localStorage + backend sync)
- [x] User authentication (register, login, JWT)
- [x] User profile management
- [x] Order history and tracking
- [x] Order creation and management
- [x] Django admin panel (product/category/order management)
- [x] Responsive design (mobile, tablet, desktop)
- [x] Image optimization and lazy loading
- [x] Inventory tracking

### Intentionally Excluded (Out of Scope)
- ❌ Payment processing (Stripe/PayPal) - Complex, separate project scope
- ❌ Shipping calculations - Business logic varies by region
- ❌ Product reviews/ratings - Future enhancement
- ❌ Email notifications - Future enhancement
- ❌ Wishlist functionality - Nice-to-have feature

### Future Enhancements
- [ ] Payment integration (Stripe)
- [ ] Product reviews and ratings
- [ ] Wishlist functionality
- [ ] Email notifications (order confirmations)
- [ ] Advanced analytics dashboard
- [ ] Multi-currency support
- [ ] Gift cards and discount codes
- [ ] Related products recommendations

## 📸 Screenshots

### Homepage & Product Catalog
![Homepage](docs/screenshots/homepage.png)

### Product Detail
![Product Detail](docs/screenshots/product-detail.png)

### Shopping Cart
![Shopping Cart](docs/screenshots/cart.png)

### Checkout & Orders
![Orders](docs/screenshots/orders.png)

## 📡 API Endpoints

### Products
```
GET    /api/products/                # List products (paginated, filtered)
GET    /api/products/{id}/           # Product detail
GET    /api/products/search/         # Search products
GET    /api/products/featured/       # Featured products
```

### Categories
```
GET    /api/categories/              # List all categories
GET    /api/categories/{id}/         # Category detail with products
```

### Cart
```
GET    /api/cart/                    # Get user's cart
POST   /api/cart/items/              # Add item to cart
PUT    /api/cart/items/{id}/         # Update cart item quantity
DELETE /api/cart/items/{id}/         # Remove item from cart
DELETE /api/cart/clear/              # Clear cart
```

### Orders
```
GET    /api/orders/                  # List user's orders
GET    /api/orders/{id}/             # Order detail
POST   /api/orders/                  # Create new order (checkout)
```

### Authentication
```
POST   /api/auth/register/           # User registration
POST   /api/auth/login/              # User login (get JWT tokens)
POST   /api/auth/refresh/            # Refresh access token
POST   /api/auth/logout/             # Logout (blacklist token)
GET    /api/auth/user/               # Get current user profile
PUT    /api/auth/user/               # Update user profile
```

## 💻 Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker (optional)

### Backend Setup
```bash
# Clone repository
git clone https://github.com/yourusername/ecommerce-product-catalog.git
cd ecommerce-product-catalog

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Load sample data
python manage.py loaddata fixtures/categories.json
python manage.py loaddata fixtures/products.json

# Run development server
python manage.py runserver
```

Backend will be available at `http://localhost:8000`  
Admin panel at `http://localhost:8000/admin`  
API docs at `http://localhost:8000/api/docs/`

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your API URL

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Docker Setup (Recommended)
```bash
# From project root
docker-compose up --build

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load sample data
docker-compose exec backend python manage.py loaddata fixtures/categories.json
docker-compose exec backend python manage.py loaddata fixtures/products.json
```

Access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Admin: http://localhost:8000/admin

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pytest --cov=. --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Specific Test Suites
```bash
# Backend
pytest tests/test_products.py          # Product tests
pytest tests/test_cart.py              # Cart functionality
pytest tests/test_orders.py            # Order processing
pytest tests/test_auth.py              # Authentication

# Frontend
npm test -- products                   # Product components
npm test -- cart                       # Cart functionality
```

## 🔐 Environment Variables

### Backend (.env)
```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_db

# JWT
JWT_SECRET_KEY=your-jwt-secret
ACCESS_TOKEN_LIFETIME=60  # minutes
REFRESH_TOKEN_LIFETIME=1440  # minutes (24 hours)

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://ecommerce-catalog.vercel.app

# Media Files
MEDIA_URL=/media/
MEDIA_ROOT=media/

# Email (for future use)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_MEDIA_URL=http://localhost:8000/media
```

## 📦 Deployment

### Backend (Railway)

1. **Create Railway project and add PostgreSQL**
```bash
   railway init
   railway add postgresql
```

2. **Set environment variables** in Railway dashboard
   - Add all backend environment variables
   - Set `DEBUG=False`
   - Update `ALLOWED_HOSTS` with production domain
   - Update `CORS_ALLOWED_ORIGINS`

3. **Deploy**
```bash
   railway up
```

4. **Run migrations and collect static files**
```bash
   railway run python manage.py migrate
   railway run python manage.py collectstatic --noinput
   railway run python manage.py createsuperuser
```

### Frontend (Vercel)

1. **Connect repository to Vercel**
2. **Configure build settings**:
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Root Directory: `frontend`
3. **Set environment variables**:
   - `VITE_API_URL`: Your Railway backend URL
   - `VITE_MEDIA_URL`: Your Railway media URL
4. Deploy automatically on push to `main`

## 📁 Project Structure
```
ecommerce-product-catalog/
├── backend/                          # Django backend
│   ├── config/                       # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── products/                     # Products app
│   │   ├── models.py                 # Product, Category models
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── filters.py                # Product filtering
│   │   └── admin.py                  # Admin configuration
│   ├── cart/                         # Shopping cart app
│   │   ├── models.py                 # Cart, CartItem models
│   │   ├── serializers.py
│   │   └── views.py
│   ├── orders/                       # Orders app
│   │   ├── models.py                 # Order, OrderItem models
│   │   ├── serializers.py
│   │   └── views.py
│   ├── users/                        # Custom user app
│   │   ├── models.py
│   │   ├── serializers.py
│   │   └── views.py
│   ├── fixtures/                     # Sample data
│   │   ├── categories.json
│   │   └── products.json
│   ├── media/                        # User-uploaded files
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── products/             # Product components
│   │   │   │   ├── ProductCard.tsx
│   │   │   │   ├── ProductGrid.tsx
│   │   │   │   ├── ProductDetail.tsx
│   │   │   │   └── ProductFilters.tsx
│   │   │   ├── cart/                 # Cart components
│   │   │   │   ├── CartDrawer.tsx
│   │   │   │   ├── CartItem.tsx
│   │   │   │   └── CartSummary.tsx
│   │   │   ├── checkout/             # Checkout components
│   │   │   │   ├── CheckoutForm.tsx
│   │   │   │   └── OrderSummary.tsx
│   │   │   ├── layout/               # Layout components
│   │   │   │   ├── Navigation.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   └── Footer.tsx
│   │   │   └── common/               # Reusable components
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   ├── ProductsPage.tsx
│   │   │   ├── ProductDetailPage.tsx
│   │   │   ├── CartPage.tsx
│   │   │   ├── CheckoutPage.tsx
│   │   │   ├── OrdersPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   └── RegisterPage.tsx
│   │   ├── contexts/                 # React contexts
│   │   │   ├── AuthContext.tsx
│   │   │   └── CartContext.tsx
│   │   ├── hooks/                    # Custom hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useCart.ts
│   │   │   └── useProducts.ts
│   │   ├── services/                 # API services
│   │   │   └── api.ts
│   │   ├── types/                    # TypeScript types
│   │   │   └── index.ts
│   │   ├── utils/                    # Utility functions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🗄️ Database Schema

### Key Models

**Product**
```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    inventory_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
```

**Cart & CartItem**
```python
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
```

**Order & OrderItem**
```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
```

## 🎨 Key Technical Highlights

### Smart Shopping Cart
- Syncs between localStorage and backend
- Persists across sessions
- Real-time inventory checking
- Quantity validation

### Advanced Product Filtering
```python
# backend/products/filters.py
from django_filters import rest_framework as filters

class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = filters.CharFilter(field_name='category__slug')
    search = filters.CharFilter(method='search_products')
    
    class Meta:
        model = Product
        fields = ['category', 'featured', 'is_active']
```

### JWT Authentication Flow
```typescript
// frontend/src/contexts/AuthContext.tsx
export function AuthProvider({ children }) {
  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login/', { email, password });
    const { access, refresh } = response.data;
    
    // Store tokens securely
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    // Set default auth header
    api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
  };
  
  // Token refresh logic, logout, etc.
}
```

## 🔒 Security Features

- JWT authentication with refresh tokens
- Password hashing with Django's PBKDF2
- CORS configuration for production
- SQL injection prevention (Django ORM)
- XSS protection (React default escaping)
- CSRF protection for forms
- Rate limiting on authentication endpoints
- Secure password reset flow (future)

## 📊 Admin Panel Features

Access at `/admin` with superuser credentials:
- **Product Management**: Add, edit, delete products
- **Category Management**: Organize product categories
- **Order Management**: View and update order statuses
- **User Management**: View user accounts and activity
- **Inventory Tracking**: Monitor stock levels
- **Bulk Actions**: Update multiple products at once

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Fabio [Your Last Name]**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Portfolio: [fabio-portfolio.vercel.app](https://fabio-portfolio.vercel.app)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Built with [Django](https://www.djangoproject.com/) and [React](https://react.dev/)
- UI components from [Material-UI](https://mui.com/)
- Deployment on [Railway](https://railway.app/) and [Vercel](https://vercel.com/)
- Product images from [Unsplash](https://unsplash.com/)

## 🌟 Show Your Support

Give a ⭐️ if this project helped you learn something new!

---

**Live Demo**: 🚀 https://ecommerce-catalog.vercel.app  
**Admin Panel**: 🔐 https://ecommerce-api.railway.app/admin  
**API Documentation**: 📚 https://ecommerce-api.railway.app/api/docs
