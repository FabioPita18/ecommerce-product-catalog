/**
 * Protected Route Component
 *
 * Wraps routes that require authentication. If the user is not logged in,
 * they are redirected to the login page. The current location is saved
 * in router state so the user can be redirected back after logging in.
 *
 * While the auth state is loading (checking for stored session on app startup),
 * a loading spinner is shown instead of redirecting.
 *
 * Usage in App.tsx:
 *   <Route path="/cart" element={
 *     <ProtectedRoute><CartPage /></ProtectedRoute>
 *   } />
 *
 * React Router protected routes: https://reactrouter.com/en/main/start/concepts#protected-routes
 */
import { Navigate, useLocation } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import { useAuth } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  // Show spinner while checking auth state on app startup
  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="50vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  // Redirect to login with the attempted URL saved in state
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // User is authenticated - render the protected content
  return <>{children}</>;
}
