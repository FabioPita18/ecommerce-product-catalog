/**
 * Orders Service
 *
 * Handles all order-related API calls:
 * - List user's orders (order history)
 * - Get order detail
 * - Create order (checkout from cart)
 *
 * All order endpoints require authentication.
 * Creating an order converts the user's cart into an order,
 * creating OrderItems from CartItems and clearing the cart.
 *
 * Backend endpoints: /api/orders/ (see backend/orders/urls.py)
 */
import api from './api';
import type { Order, OrderListItem, CreateOrderData } from '@/types';

export const ordersService = {
  /**
   * Get the user's order history.
   * Returns lightweight order list items (no nested items).
   * GET /api/orders/
   */
  async getOrders(): Promise<OrderListItem[]> {
    const response = await api.get<OrderListItem[]>('/orders/');
    return response.data;
  },

  /**
   * Get full order details including items.
   * GET /api/orders/{id}/
   */
  async getOrder(id: number): Promise<Order> {
    const response = await api.get<Order>(`/orders/${id}/`);
    return response.data;
  },

  /**
   * Create a new order from the current cart (checkout).
   * The backend will:
   * 1. Validate the cart has items and inventory is available
   * 2. Create Order + OrderItems from cart
   * 3. Deduct inventory
   * 4. Clear the cart
   * POST /api/orders/
   */
  async createOrder(data: CreateOrderData): Promise<Order> {
    const response = await api.post<Order>('/orders/', data);
    return response.data;
  },
};
