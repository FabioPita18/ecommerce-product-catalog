/**
 * Hook for consuming auth context.
 *
 * Separated from AuthContext.tsx so that the context file only exports
 * components (required by React fast-refresh / react-refresh ESLint rule).
 *
 * Usage:
 *   const { user, login, logout, isAuthenticated } = useAuth();
 */
import { useContext } from 'react';
import { AuthContext } from '@/contexts/authContextDef';
import type { AuthContextType } from '@/contexts/authContextDef';

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
