/**
 * Product & Category Query Hooks
 *
 * TanStack Query hooks for fetching product and category data.
 * Each hook wraps a service call with caching, loading states, and error handling.
 *
 * Key concepts:
 * - queryKey: Unique identifier for cached data. When the key changes,
 *   TanStack Query knows to refetch.
 * - staleTime: How long cached data is considered "fresh". During this time,
 *   components get instant data from cache without refetching.
 * - enabled: Conditionally run the query (e.g., only fetch when we have a slug).
 *
 * TanStack Query docs: https://tanstack.com/query/latest
 */
import { useQuery } from '@tanstack/react-query';
import { productsService } from '@/services/products';
import type { ProductFilters } from '@/types';

// ---------------------------------------------------------------------------
// Query Key Factories
// ---------------------------------------------------------------------------

/**
 * Query key factory for products.
 * Using a factory ensures consistent keys across the app.
 * Keys are hierarchical: invalidating ['products'] invalidates all product queries.
 */
export const productKeys = {
  all: ['products'] as const,
  lists: () => [...productKeys.all, 'list'] as const,
  list: (filters?: ProductFilters) =>
    [...productKeys.lists(), filters] as const,
  details: () => [...productKeys.all, 'detail'] as const,
  detail: (slug: string) => [...productKeys.details(), slug] as const,
  featured: () => [...productKeys.all, 'featured'] as const,
};

/** Query key factory for categories. */
export const categoryKeys = {
  all: ['categories'] as const,
  lists: () => [...categoryKeys.all, 'list'] as const,
  detail: (slug: string) => [...categoryKeys.all, 'detail', slug] as const,
};

// ---------------------------------------------------------------------------
// Product Hooks
// ---------------------------------------------------------------------------

/**
 * Fetch paginated products list with optional filters.
 * Re-fetches when filters change (because the queryKey includes filters).
 */
export function useProducts(filters?: ProductFilters) {
  return useQuery({
    queryKey: productKeys.list(filters),
    queryFn: () => productsService.getProducts(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes - products don't change often
  });
}

/**
 * Fetch a single product by slug.
 * Only runs when slug is truthy (avoids fetching with empty string).
 */
export function useProduct(slug: string) {
  return useQuery({
    queryKey: productKeys.detail(slug),
    queryFn: () => productsService.getProduct(slug),
    enabled: !!slug,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Fetch featured products for the homepage.
 * Longer stale time since featured products rarely change.
 */
export function useFeaturedProducts() {
  return useQuery({
    queryKey: productKeys.featured(),
    queryFn: () => productsService.getFeaturedProducts(),
    staleTime: 5 * 60 * 1000,
  });
}

// ---------------------------------------------------------------------------
// Category Hooks
// ---------------------------------------------------------------------------

/**
 * Fetch all categories.
 * Long stale time since categories rarely change.
 */
export function useCategories() {
  return useQuery({
    queryKey: categoryKeys.lists(),
    queryFn: () => productsService.getCategories(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Fetch a single category by slug.
 */
export function useCategory(slug: string) {
  return useQuery({
    queryKey: categoryKeys.detail(slug),
    queryFn: () => productsService.getCategory(slug),
    enabled: !!slug,
    staleTime: 10 * 60 * 1000,
  });
}
