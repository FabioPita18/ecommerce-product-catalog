/**
 * Cart Service
 *
 * Handles all shopping cart API calls:
 * - Get cart with items and totals
 * - Get lightweight cart summary (for navbar badge)
 * - Add/update/remove cart items
 * - Clear entire cart
 *
 * All cart endpoints require authentication.
 * The backend creates a cart lazily when the first item is added.
 *
 * Backend endpoints: /api/cart/ (see backend/cart/urls.py)
 */
import api from './api';
import type { Cart, CartItem, CartSummary, AddToCartData } from '@/types';

export const cartService = {
  /**
   * Get the full cart with all items and computed totals.
   * GET /api/cart/
   */
  async getCart(): Promise<Cart> {
    const response = await api.get<Cart>('/cart/');
    return response.data;
  },

  /**
   * Get lightweight cart summary (item count + total amount).
   * Used by the navbar badge - avoids fetching full cart data.
   * GET /api/cart/summary/
   */
  async getCartSummary(): Promise<CartSummary> {
    const response = await api.get<CartSummary>('/cart/summary/');
    return response.data;
  },

  /**
   * Add an item to the cart.
   * If the product is already in the cart, the backend updates the quantity.
   * POST /api/cart/items/
   */
  async addToCart(data: AddToCartData): Promise<CartItem> {
    const response = await api.post<CartItem>('/cart/items/', data);
    return response.data;
  },

  /**
   * Update the quantity of a cart item.
   * PATCH /api/cart/items/{id}/
   */
  async updateCartItem(itemId: number, quantity: number): Promise<CartItem> {
    const response = await api.patch<CartItem>(`/cart/items/${itemId}/`, {
      quantity,
    });
    return response.data;
  },

  /**
   * Remove an item from the cart.
   * DELETE /api/cart/items/{id}/
   */
  async removeCartItem(itemId: number): Promise<void> {
    await api.delete(`/cart/items/${itemId}/`);
  },

  /**
   * Clear the entire cart (remove all items).
   * DELETE /api/cart/
   */
  async clearCart(): Promise<void> {
    await api.delete('/cart/');
  },
};
