/**
 * TypeScript Type Definitions
 *
 * These types MUST match the backend Django REST Framework serializers.
 * When the backend serializer fields change, update these immediately.
 *
 * The backend uses snake_case for field names (Django convention).
 * We keep snake_case here to avoid needing a transformation layer,
 * since the Axios responses will contain snake_case keys directly.
 *
 * Alternative: Use a library like axios-case-converter to auto-convert
 * snake_case <-> camelCase. We chose not to, for simplicity and transparency.
 */

// =============================================================================
// User Types
// =============================================================================

/**
 * User profile as returned by GET /api/auth/profile/
 * Matches backend UserProfileSerializer fields.
 */
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
  last_login: string | null;
}

/**
 * JWT token pair returned on login/register.
 */
export interface AuthTokens {
  access: string;
  refresh: string;
}

/**
 * Login response includes both tokens and user data.
 * Matches backend TokenResponseSerializer.
 */
export interface LoginResponse extends AuthTokens {
  user: User;
}

/**
 * Data required for user registration.
 * Matches backend UserRegistrationSerializer.
 */
export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
}

// =============================================================================
// Product Types
// =============================================================================

/**
 * Category as returned by the backend CategorySerializer.
 * Used both standalone and nested within product responses.
 */
export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  image: string | null;
  product_count?: number;
}

/**
 * Full product detail as returned by GET /api/products/{slug}/
 * Matches backend ProductDetailSerializer.
 *
 * Note: price is a string because Django's DecimalField serializes to string
 * to preserve precision. Parse to number when needed for calculations.
 * Note: The backend field is "featured" (not "is_featured").
 */
export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: string;
  category: Category;
  image: string | null;
  inventory_count: number;
  is_active: boolean;
  featured: boolean;
  is_in_stock: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Lightweight product for list views.
 * Matches backend ProductListSerializer - fewer fields for performance.
 */
export interface ProductListItem {
  id: number;
  name: string;
  slug: string;
  price: string;
  category: Category;
  image: string | null;
  is_in_stock: boolean;
  featured: boolean;
}

/**
 * Query parameters for filtering products.
 * Matches backend ProductFilter fields from django-filter.
 */
export interface ProductFilters {
  category?: string;
  min_price?: number;
  max_price?: number;
  in_stock?: boolean;
  featured?: boolean;
  search?: string;
  ordering?: string;
  page?: number;
}

// =============================================================================
// Cart Types
// =============================================================================

/**
 * Cart item with nested product data.
 * Matches backend CartItemSerializer.
 */
export interface CartItem {
  id: number;
  product: ProductListItem;
  quantity: number;
  subtotal: string;
}

/**
 * Full cart with items and computed totals.
 * Matches backend CartSerializer.
 */
export interface Cart {
  id: number;
  items: CartItem[];
  total_items: number;
  total_amount: string;
  updated_at: string;
}

/**
 * Lightweight cart summary for the navbar badge.
 * Matches backend CartSummarySerializer.
 */
export interface CartSummary {
  total_items: number;
  total_amount: string;
}

/**
 * Data for adding an item to cart.
 * Matches backend CartItemCreateSerializer.
 */
export interface AddToCartData {
  product_id: number;
  quantity: number;
}

// =============================================================================
// Order Types
// =============================================================================

/**
 * Possible order statuses matching backend Order.STATUS_CHOICES.
 */
export type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';

/**
 * Order item with product snapshot and price at time of purchase.
 * Matches backend OrderItemSerializer.
 */
export interface OrderItem {
  id: number;
  product: ProductListItem;
  quantity: number;
  price_at_purchase: string;
  subtotal: string;
}

/**
 * Full order detail as returned by GET /api/orders/{id}/
 * Matches backend OrderDetailSerializer.
 */
export interface Order {
  id: number;
  status: OrderStatus;
  status_display: string;
  total_amount: string;
  shipping_address: string;
  notes: string;
  items: OrderItem[];
  item_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * Lightweight order for list views.
 * Matches backend OrderListSerializer.
 */
export interface OrderListItem {
  id: number;
  status: OrderStatus;
  status_display: string;
  total_amount: string;
  item_count: number;
  created_at: string;
}

/**
 * Data for creating an order (checkout).
 * Matches backend OrderCreateSerializer.
 */
export interface CreateOrderData {
  shipping_address: string;
  notes?: string;
}

// =============================================================================
// API Types
// =============================================================================

/**
 * Django REST Framework's default pagination response shape.
 * Used by any endpoint with PageNumberPagination.
 */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/**
 * Common API error response shape.
 * DRF returns { detail: "..." } for most errors,
 * or { field_name: ["error message"] } for validation errors.
 */
export interface ApiError {
  detail?: string;
  [key: string]: unknown;
}
