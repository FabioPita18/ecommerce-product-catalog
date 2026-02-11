/**
 * Login Page
 *
 * Allows users to log in with email and password.
 * Full form validation with react-hook-form + zod will be added in Phase 7.
 *
 * Current placeholder features:
 * - Email and password fields
 * - Submit button with loading state
 * - Link to register page
 * - Redirects to previous page after login (using router state)
 */
import { useState } from 'react';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Paper,
  Alert,
  Link,
} from '@mui/material';
import { useAuth } from '@/contexts/AuthContext';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Where to redirect after login (defaults to home)
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch {
      setError('Invalid email or password. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" textAlign="center" gutterBottom>
          Login
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            fullWidth
          />
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={isSubmitting}
            fullWidth
          >
            {isSubmitting ? 'Logging in...' : 'Login'}
          </Button>
        </Box>

        <Typography textAlign="center" sx={{ mt: 2 }}>
          Don&apos;t have an account?{' '}
          <Link component={RouterLink} to="/register">
            Register
          </Link>
        </Typography>
      </Paper>
    </Container>
  );
}
