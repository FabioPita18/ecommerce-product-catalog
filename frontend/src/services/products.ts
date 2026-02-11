/**
 * Products & Categories Service
 *
 * Handles all product-related API calls:
 * - Product listing with filters and pagination
 * - Product detail by slug
 * - Featured products
 * - Category listing and detail
 *
 * Backend endpoints:
 *   /api/products/  (see backend/products/urls.py)
 *   /api/categories/
 *
 * Note: The categories endpoint returns a paginated response (DRF default).
 * We extract the results array for convenience since there are typically
 * few categories and we want them all.
 */
import api from './api';
import type {
  Product,
  ProductListItem,
  Category,
  ProductFilters,
  PaginatedResponse,
} from '@/types';

export const productsService = {
  /**
   * Get paginated list of products with optional filters.
   * Filters are passed as query parameters to django-filter.
   */
  async getProducts(
    filters?: ProductFilters
  ): Promise<PaginatedResponse<ProductListItem>> {
    const params = new URLSearchParams();

    if (filters) {
      // Convert filter object to query params, skipping empty values
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value));
        }
      });
    }

    const response = await api.get<PaginatedResponse<ProductListItem>>(
      '/products/',
      { params }
    );
    return response.data;
  },

  /**
   * Get full product detail by slug.
   * The backend uses slug-based lookup for SEO-friendly URLs.
   */
  async getProduct(slug: string): Promise<Product> {
    const response = await api.get<Product>(`/products/${slug}/`);
    return response.data;
  },

  /**
   * Get featured products (max 8).
   * Returns a flat array (not paginated) from the custom action endpoint.
   */
  async getFeaturedProducts(): Promise<ProductListItem[]> {
    const response = await api.get<ProductListItem[]>('/products/featured/');
    return response.data;
  },

  /**
   * Get all categories.
   * The backend returns a paginated response, but we extract just the results
   * since there are typically few categories.
   */
  async getCategories(): Promise<Category[]> {
    const response =
      await api.get<PaginatedResponse<Category>>('/categories/');
    return response.data.results;
  },

  /**
   * Get a single category by slug, including its products.
   */
  async getCategory(slug: string): Promise<Category> {
    const response = await api.get<Category>(`/categories/${slug}/`);
    return response.data;
  },
};
