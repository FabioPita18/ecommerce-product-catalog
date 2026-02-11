/**
 * Register Page
 *
 * Allows new users to create an account.
 * Full form validation with react-hook-form + zod will be added in Phase 7.
 *
 * Current placeholder features:
 * - Registration form fields (name, email, password)
 * - Submit button with loading state
 * - Link to login page
 * - Auto-login after successful registration
 */
import { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
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

export function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    password_confirm: '',
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.password_confirm) {
      setError('Passwords do not match.');
      return;
    }

    setIsSubmitting(true);

    try {
      await register(formData);
      navigate('/', { replace: true });
    } catch {
      setError('Registration failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" textAlign="center" gutterBottom>
          Create Account
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              label="First Name"
              value={formData.first_name}
              onChange={handleChange('first_name')}
              required
              fullWidth
            />
            <TextField
              label="Last Name"
              value={formData.last_name}
              onChange={handleChange('last_name')}
              required
              fullWidth
            />
          </Box>
          <TextField
            label="Email"
            type="email"
            value={formData.email}
            onChange={handleChange('email')}
            required
            fullWidth
          />
          <TextField
            label="Password"
            type="password"
            value={formData.password}
            onChange={handleChange('password')}
            required
            fullWidth
          />
          <TextField
            label="Confirm Password"
            type="password"
            value={formData.password_confirm}
            onChange={handleChange('password_confirm')}
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
            {isSubmitting ? 'Creating account...' : 'Register'}
          </Button>
        </Box>

        <Typography textAlign="center" sx={{ mt: 2 }}>
          Already have an account?{' '}
          <Link component={RouterLink} to="/login">
            Login
          </Link>
        </Typography>
      </Paper>
    </Container>
  );
}
