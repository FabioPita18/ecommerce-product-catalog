/**
 * Orders Query & Mutation Hooks
 *
 * TanStack Query hooks for order operations.
 * Orders are read-heavy (list + detail) with one mutation (create order).
 *
 * Creating an order also invalidates cart queries because the backend
 * clears the cart during checkout.
 *
 * TanStack Query docs: https://tanstack.com/query/latest
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ordersService } from '@/services/orders';
import { cartKeys } from './useCart';
import type { CreateOrderData } from '@/types';

// ---------------------------------------------------------------------------
// Query Key Factory
// ---------------------------------------------------------------------------

export const orderKeys = {
  all: ['orders'] as const,
  lists: () => [...orderKeys.all, 'list'] as const,
  detail: (id: number) => [...orderKeys.all, 'detail', id] as const,
};

// ---------------------------------------------------------------------------
// Query Hooks (Read)
// ---------------------------------------------------------------------------

/**
 * Fetch the user's order history.
 */
export function useOrders() {
  return useQuery({
    queryKey: orderKeys.lists(),
    queryFn: () => ordersService.getOrders(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Fetch a single order by ID.
 * Only runs when id is truthy (non-zero).
 */
export function useOrder(id: number) {
  return useQuery({
    queryKey: orderKeys.detail(id),
    queryFn: () => ordersService.getOrder(id),
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  });
}

// ---------------------------------------------------------------------------
// Mutation Hooks (Write)
// ---------------------------------------------------------------------------

/**
 * Create a new order (checkout).
 * On success, invalidates both order and cart queries because
 * the backend clears the cart after creating an order.
 */
export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateOrderData) => ordersService.createOrder(data),
    onSuccess: () => {
      // Refresh order list to include the new order
      queryClient.invalidateQueries({ queryKey: orderKeys.all });
      // Cart was cleared by the backend during checkout
      queryClient.invalidateQueries({ queryKey: cartKeys.all });
    },
  });
}
