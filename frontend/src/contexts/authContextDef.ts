/**
 * Auth Context Definition
 *
 * The context object and its type are in this separate file so that
 * AuthContext.tsx only exports React components (required by the
 * react-refresh ESLint rule for fast refresh to work correctly).
 *
 * Both AuthContext.tsx (provider) and useAuth.ts (consumer hook)
 * import from this file.
 */
import { createContext } from 'react';
import type { User, LoginResponse, RegisterData } from '@/types';

export interface AuthContextType {
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

export const AuthContext = createContext<AuthContextType | undefined>(undefined);
