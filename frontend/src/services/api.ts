/**
 * API Service Layer - Centralized Axios Instance
 *
 * This module creates and configures a single Axios instance used by all
 * service modules. It handles:
 *
 * 1. Base URL: All requests go through /api (proxied to Django in development)
 * 2. JWT injection: Automatically adds Authorization header to requests
 * 3. Token refresh: On 401 responses, tries to refresh the access token
 *    before redirecting to login
 * 4. Token storage: Access token in memory (more secure), refresh token
 *    in localStorage (persists across page refreshes)
 *
 * Why not store access token in localStorage?
 *   localStorage is vulnerable to XSS attacks. Keeping the access token
 *   in memory means it's lost on page refresh, but we can silently refresh
 *   using the stored refresh token. This is a common security pattern.
 *
 * Axios docs: https://axios-http.com/docs/intro
 */
import axios from 'axios';
import type { AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = '/api';

// Create Axios instance with default configuration
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ---------------------------------------------------------------------------
// Token Management
// ---------------------------------------------------------------------------

// Access token stored in memory (not localStorage) for security
let accessToken: string | null = null;
// Refresh token stored both in memory and localStorage for persistence
let refreshToken: string | null = null;

/**
 * Store both tokens after login/register.
 * Access token stays in memory; refresh token goes to localStorage
 * so we can restore the session after page refresh.
 */
export const setTokens = (access: string, refresh: string): void => {
  accessToken = access;
  refreshToken = refresh;
  localStorage.setItem('refreshToken', refresh);
};

/** Get current access token (for debugging or manual use). */
export const getAccessToken = (): string | null => accessToken;

/** Clear all tokens - used on logout or when refresh fails. */
export const clearTokens = (): void => {
  accessToken = null;
  refreshToken = null;
  localStorage.removeItem('refreshToken');
};

/**
 * Load refresh token from localStorage on app startup.
 * This allows restoring the session after a page refresh.
 */
export const loadStoredRefreshToken = (): string | null => {
  refreshToken = localStorage.getItem('refreshToken');
  return refreshToken;
};

// ---------------------------------------------------------------------------
// Request Interceptor - Inject JWT Token
// ---------------------------------------------------------------------------

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add Authorization header if we have an access token
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ---------------------------------------------------------------------------
// Response Interceptor - Handle 401 with Token Refresh
// ---------------------------------------------------------------------------

api.interceptors.response.use(
  // Success - pass through
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // If we got a 401 and have a refresh token, try to get a new access token
    // The _retry flag prevents infinite loops if the refresh also returns 401
    if (
      error.response?.status === 401 &&
      refreshToken &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      try {
        // Use a fresh axios instance (not our api instance) to avoid
        // triggering interceptors recursively
        const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        accessToken = access;

        // Retry the original request with the new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access}`;
        }
        return api(originalRequest);
      } catch {
        // Refresh token is also invalid - user needs to log in again
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
