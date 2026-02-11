/**
 * Authentication Service
 *
 * Handles all authentication-related API calls:
 * - Login/Register: Get JWT tokens and user profile
 * - Logout: Blacklist refresh token on the server
 * - Profile: Get/update user profile
 * - Session refresh: Restore session from stored refresh token
 * - Password change: Update user password
 *
 * This service works with the AuthContext to manage authentication state.
 * Token management is handled by the api module (services/api.ts).
 *
 * Backend endpoints: /api/auth/ (see backend/users/urls.py)
 */
import api, { setTokens, clearTokens, loadStoredRefreshToken } from './api';
import type { User, LoginResponse, RegisterData } from '@/types';

export const authService = {
  /**
   * Log in with email and password.
   * Returns tokens + user data, and stores tokens via setTokens.
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login/', {
      email,
      password,
    });
    setTokens(response.data.access, response.data.refresh);
    return response.data;
  },

  /**
   * Register a new account.
   * Backend auto-logs in the user by returning tokens + user data.
   */
  async register(data: RegisterData): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/register/', data);
    setTokens(response.data.access, response.data.refresh);
    return response.data;
  },

  /**
   * Log out by blacklisting the refresh token on the server.
   * Always clears local tokens even if the API call fails.
   */
  async logout(refresh: string): Promise<void> {
    try {
      await api.post('/auth/logout/', { refresh });
    } finally {
      clearTokens();
    }
  },

  /**
   * Get the current user's profile.
   * Requires a valid access token.
   */
  async getProfile(): Promise<User> {
    const response = await api.get<User>('/auth/profile/');
    return response.data;
  },

  /**
   * Try to restore a session from a stored refresh token.
   * Called on app startup to check if the user is still logged in.
   *
   * Flow:
   * 1. Load refresh token from localStorage
   * 2. Exchange it for a new access token
   * 3. Fetch the user profile
   * 4. Return user (or null if any step fails)
   */
  async refreshSession(): Promise<User | null> {
    const storedRefresh = loadStoredRefreshToken();
    if (!storedRefresh) return null;

    try {
      const response = await api.post('/auth/refresh/', {
        refresh: storedRefresh,
      });
      setTokens(response.data.access, storedRefresh);
      return await this.getProfile();
    } catch {
      clearTokens();
      return null;
    }
  },

  /**
   * Update user profile (first_name, last_name).
   * Uses PATCH for partial updates.
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.patch<User>('/auth/profile/', data);
    return response.data;
  },

  /**
   * Change the user's password.
   * Requires the current password for verification.
   */
  async changePassword(
    currentPassword: string,
    newPassword: string,
    newPasswordConfirm: string
  ): Promise<void> {
    await api.post('/auth/password/change/', {
      current_password: currentPassword,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    });
  },
};
