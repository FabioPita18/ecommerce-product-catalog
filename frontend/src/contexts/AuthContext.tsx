/**
 * Authentication Context
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
 * React Context docs: https://react.dev/reference/react/createContext
 */
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from 'react';
import type { ReactNode } from 'react';
import { authService } from '@/services/auth';
import { clearTokens } from '@/services/api';
import type { User, LoginResponse, RegisterData } from '@/types';

// ---------------------------------------------------------------------------
// Context Type Definition
// ---------------------------------------------------------------------------

interface AuthContextType {
  /** Current user, or null if not logged in */
  user: User | null;
  /** True while checking for existing session on app startup */
  isLoading: boolean;
  /** Convenience boolean - true if user is not null */
  isAuthenticated: boolean;
  /** Log in with email/password, returns tokens + user */
  login: (email: string, password: string) => Promise<LoginResponse>;
  /** Register a new account, returns tokens + user */
  register: (data: RegisterData) => Promise<LoginResponse>;
  /** Log out and clear all tokens */
  logout: () => Promise<void>;
  /** Re-fetch user profile (e.g., after profile update) */
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

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

  const value: AuthContextType = {
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

// ---------------------------------------------------------------------------
// Hook for consuming auth context
// ---------------------------------------------------------------------------

/**
 * Hook to access auth state and actions.
 * Must be used within an AuthProvider.
 *
 * Usage:
 *   const { user, login, logout, isAuthenticated } = useAuth();
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
