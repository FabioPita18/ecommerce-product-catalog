/**
 * Registration Page
 *
 * Allows new users to create an account.
 * Uses react-hook-form for form state and zod for comprehensive validation.
 *
 * Validation rules:
 * - Email must be valid format
 * - First/last name required
 * - Password: min 8 chars, must contain uppercase letter and number
 * - Password confirmation must match
 *
 * On success, the user is auto-logged in (backend returns tokens)
 * and redirected to the home page.
 *
 * react-hook-form docs: https://react-hook-form.com/
 */
import { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Link,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { useAuth } from '@/contexts/AuthContext';

/**
 * Zod schema for registration form.
 * Uses .refine() for cross-field validation (password confirmation).
 */
const registerSchema = z
  .object({
    email: z.string().email('Invalid email address'),
    first_name: z.string().min(1, 'First name is required'),
    last_name: z.string().min(1, 'Last name is required'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain an uppercase letter')
      .regex(/[0-9]/, 'Password must contain a number'),
    password_confirm: z.string(),
  })
  .refine((data) => data.password === data.password_confirm, {
    message: 'Passwords do not match',
    path: ['password_confirm'],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const navigate = useNavigate();
  const { register: registerUser } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setError(null);
    setIsLoading(true);

    try {
      await registerUser(data);
      navigate('/');
    } catch (err: unknown) {
      // DRF returns validation errors as { field: ["message"] }
      const errorData = (
        err as { response?: { data?: Record<string, string[]> } }
      )?.response?.data;
      if (errorData) {
        const messages = Object.values(errorData).flat().join(', ');
        setError(messages);
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          textAlign="center"
          gutterBottom
        >
          Create Account
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
          {/* Name fields side by side */}
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                {...register('first_name')}
                label="First Name"
                fullWidth
                error={!!errors.first_name}
                helperText={errors.first_name?.message}
                autoFocus
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                {...register('last_name')}
                label="Last Name"
                fullWidth
                error={!!errors.last_name}
                helperText={errors.last_name?.message}
              />
            </Grid>
          </Grid>

          <TextField
            {...register('email')}
            label="Email"
            type="email"
            fullWidth
            margin="normal"
            error={!!errors.email}
            helperText={errors.email?.message}
            autoComplete="email"
          />

          <TextField
            {...register('password')}
            label="Password"
            type="password"
            fullWidth
            margin="normal"
            error={!!errors.password}
            helperText={errors.password?.message}
            autoComplete="new-password"
          />

          <TextField
            {...register('password_confirm')}
            label="Confirm Password"
            type="password"
            fullWidth
            margin="normal"
            error={!!errors.password_confirm}
            helperText={errors.password_confirm?.message}
            autoComplete="new-password"
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={isLoading}
            sx={{ mt: 3, mb: 2 }}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Register'}
          </Button>

          <Typography textAlign="center">
            Already have an account?{' '}
            <Link component={RouterLink} to="/login">
              Login here
            </Link>
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}
