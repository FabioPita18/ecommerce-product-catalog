/**
 * Main Application Component
 *
 * This is the root component that sets up all providers and routing.
 * The provider hierarchy matters - each provider can only access
 * providers that wrap it (outer providers).
 *
 * Provider order (outermost to innermost):
 * 1. QueryClientProvider - TanStack Query cache (no dependencies)
 * 2. ThemeProvider + CssBaseline - MUI theme (no dependencies)
 * 3. SnackbarProvider - Toast notifications (needs theme)
 * 4. AuthProvider - Auth state (needs QueryClient for hooks)
 * 5. BrowserRouter - Routing (needs auth for ProtectedRoute)
 *
 * React Router docs: https://reactrouter.com/
 * TanStack Query docs: https://tanstack.com/query/latest
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { SnackbarProvider } from 'notistack';
import { theme } from '@/theme';
import { AuthProvider } from '@/contexts/AuthContext';
import { Navbar } from '@/components/common/Navbar';
import { ProtectedRoute } from '@/components/common/ProtectedRoute';

// Pages
import { HomePage } from '@/pages/HomePage';
import { ProductsPage } from '@/pages/ProductsPage';
import { ProductDetailPage } from '@/pages/ProductDetailPage';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { CartPage } from '@/pages/CartPage';
import { CheckoutPage } from '@/pages/CheckoutPage';
import { OrdersPage } from '@/pages/OrdersPage';
import { OrderDetailPage } from '@/pages/OrderDetailPage';

/**
 * TanStack Query client configuration.
 *
 * - retry: 1 - Retry failed requests once (default is 3, which can be slow)
 * - refetchOnWindowFocus: false - Don't refetch when user switches tabs
 *   (reduces unnecessary API calls during development)
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        {/* CssBaseline applies a consistent CSS reset across browsers */}
        <CssBaseline />
        <SnackbarProvider
          maxSnack={3}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <AuthProvider>
            <BrowserRouter>
              <Navbar />
              <Routes>
                {/* Public Routes - accessible to everyone */}
                <Route path="/" element={<HomePage />} />
                <Route path="/products" element={<ProductsPage />} />
                <Route
                  path="/products/:slug"
                  element={<ProductDetailPage />}
                />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* Protected Routes - require authentication */}
                <Route
                  path="/cart"
                  element={
                    <ProtectedRoute>
                      <CartPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/checkout"
                  element={
                    <ProtectedRoute>
                      <CheckoutPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/orders"
                  element={
                    <ProtectedRoute>
                      <OrdersPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/orders/:id"
                  element={
                    <ProtectedRoute>
                      <OrderDetailPage />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </BrowserRouter>
          </AuthProvider>
        </SnackbarProvider>
      </ThemeProvider>
      {/* React Query Devtools - only shown in development */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
