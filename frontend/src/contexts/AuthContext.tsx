/**
 * Authentication Context Provider
 *
 * Provides authentication state and actions to the entire app via React Context.
 * This is the single source of truth for "who is logged in".
 *
 * How it works:
 * 1. On mount, tries to restore a session from a stored refresh token
 * 2. Provides login/register functions that update the user state
 * 3. Provides logout that clears tokens and user state
 * 4. Shows a loading state while checking for existing session
 *
 * Why Context instead of TanStack Query for auth?
 *   Auth state is "global app state" that many components need.
 *   Context is simpler for this than query caching, and auth state
 *   doesn't benefit from TanStack Query's refetching/caching features.
 *
 * Note: The context object and type are in authContextDef.ts so this file
 * only exports components (required by react-refresh for fast refresh).
 * The useAuth hook is in hooks/useAuth.ts for the same reason.
 *
 * React Context docs: https://react.dev/reference/react/createContext
 */
import {
  useState,
  useEffect,
  useCallback,
} from 'react';
import type { ReactNode } from 'react';
import { authService } from '@/services/auth';
import { clearTokens } from '@/services/api';
import { AuthContext } from '@/contexts/authContextDef';
import type { LoginResponse, RegisterData } from '@/types';
import type { User } from '@/types';

// ---------------------------------------------------------------------------
// Provider Component
// ---------------------------------------------------------------------------

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount, check if we have a stored refresh token and try to restore session
  useEffect(() => {
    const initAuth = async () => {
      try {
        const restoredUser = await authService.refreshSession();
        setUser(restoredUser);
      } catch {
        // Session restoration failed - user needs to log in again
        clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = useCallback(
    async (email: string, password: string): Promise<LoginResponse> => {
      const response = await authService.login(email, password);
      setUser(response.user);
      return response;
    },
    []
  );

  const register = useCallback(
    async (data: RegisterData): Promise<LoginResponse> => {
      const response = await authService.register(data);
      setUser(response.user);
      return response;
    },
    []
  );

  const logout = useCallback(async (): Promise<void> => {
    const storedRefresh = localStorage.getItem('refreshToken');
    if (storedRefresh) {
      await authService.logout(storedRefresh);
    }
    setUser(null);
  }, []);

  const refreshUser = useCallback(async (): Promise<void> => {
    const updatedUser = await authService.getProfile();
    setUser(updatedUser);
  }, []);

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
