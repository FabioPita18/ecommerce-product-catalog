/**
 * Cart Query & Mutation Hooks
 *
 * TanStack Query hooks for cart operations.
 * Queries fetch cart data; mutations modify it.
 *
 * After any mutation (add, update, remove, clear), we invalidate all cart
 * queries so the UI stays in sync. This is simpler than optimistic updates
 * and avoids cache inconsistency bugs.
 *
 * All cart operations require authentication - the `enabled` flag
 * prevents queries from running for unauthenticated users.
 *
 * TanStack Query mutations: https://tanstack.com/query/latest/docs/framework/react/guides/mutations
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cartService } from '@/services/cart';
import { useAuth } from '@/contexts/AuthContext';
import type { AddToCartData } from '@/types';

// ---------------------------------------------------------------------------
// Query Key Factory
// ---------------------------------------------------------------------------

export const cartKeys = {
  all: ['cart'] as const,
  detail: () => [...cartKeys.all, 'detail'] as const,
  summary: () => [...cartKeys.all, 'summary'] as const,
};

// ---------------------------------------------------------------------------
// Query Hooks (Read)
// ---------------------------------------------------------------------------

/**
 * Fetch the full cart with items and totals.
 * Only runs when user is authenticated.
 */
export function useCart() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: cartKeys.detail(),
    queryFn: () => cartService.getCart(),
    enabled: isAuthenticated,
    staleTime: 1 * 60 * 1000, // 1 minute - cart changes frequently
  });
}

/**
 * Fetch lightweight cart summary for the navbar badge.
 * Only runs when user is authenticated.
 */
export function useCartSummary() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: cartKeys.summary(),
    queryFn: () => cartService.getCartSummary(),
    enabled: isAuthenticated,
    staleTime: 1 * 60 * 1000,
  });
}

// ---------------------------------------------------------------------------
// Mutation Hooks (Write)
// ---------------------------------------------------------------------------

/**
 * Add an item to the cart.
 * On success, invalidates all cart queries to refresh the UI.
 */
export function useAddToCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AddToCartData) => cartService.addToCart(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cartKeys.all });
    },
  });
}

/**
 * Update the quantity of a cart item.
 */
export function useUpdateCartItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      itemId,
      quantity,
    }: {
      itemId: number;
      quantity: number;
    }) => cartService.updateCartItem(itemId, quantity),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cartKeys.all });
    },
  });
}

/**
 * Remove an item from the cart.
 */
export function useRemoveCartItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemId: number) => cartService.removeCartItem(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cartKeys.all });
    },
  });
}

/**
 * Clear all items from the cart.
 */
export function useClearCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => cartService.clearCart(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cartKeys.all });
    },
  });
}
