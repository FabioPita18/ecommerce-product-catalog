/**
 * Checkout Page
 *
 * Handles the order creation process.
 * Displays an order summary from the cart and collects shipping address.
 *
 * Features:
 * - Shipping address form with zod validation
 * - Order summary showing cart items and total
 * - Place order button with loading state
 * - Error handling for failed orders
 * - Redirects to order detail page on success
 * - Empty cart guard (redirects if no items)
 *
 * The checkout flow:
 * 1. User enters shipping address
 * 2. Frontend calls POST /api/orders/ with the address
 * 3. Backend creates order from cart, deducts inventory, clears cart
 * 4. User is redirected to the new order's detail page
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Container,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Box,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { useCart } from '@/hooks/useCart';
import { useCreateOrder } from '@/hooks/useOrders';
import { useSnackbar } from 'notistack';

/**
 * Zod schema for checkout form.
 * Requires a minimum 10-character shipping address.
 */
const checkoutSchema = z.object({
  shipping_address: z
    .string()
    .min(10, 'Please enter a complete shipping address'),
});

type CheckoutFormData = z.infer<typeof checkoutSchema>;

export function CheckoutPage() {
  const navigate = useNavigate();
  const { data: cart, isLoading: cartLoading } = useCart();
  const createOrder = useCreateOrder();
  const { enqueueSnackbar } = useSnackbar();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CheckoutFormData>({
    resolver: zodResolver(checkoutSchema),
  });

  const onSubmit = async (data: CheckoutFormData) => {
    setError(null);
    try {
      const order = await createOrder.mutateAsync(data);
      enqueueSnackbar('Order placed successfully!', { variant: 'success' });
      navigate(`/orders/${order.id}`);
    } catch (err: unknown) {
      const errorMessage =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || 'Failed to place order. Please try again.';
      setError(errorMessage);
    }
  };

  // Loading state while fetching cart
  if (cartLoading) {
    return (
      <Container maxWidth="md" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  // Guard: redirect if cart is empty
  if (!cart || cart.items.length === 0) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="info">
          Your cart is empty. Please add items before checking out.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Checkout
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Shipping Address Form */}
        <Grid size={{ xs: 12, md: 7 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Shipping Address
              </Typography>
              <Box component="form" onSubmit={handleSubmit(onSubmit)}>
                <TextField
                  {...register('shipping_address')}
                  label="Full Address"
                  multiline
                  rows={4}
                  fullWidth
                  placeholder="Street address, City, State, ZIP Code, Country"
                  error={!!errors.shipping_address}
                  helperText={errors.shipping_address?.message}
                />
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  fullWidth
                  disabled={createOrder.isPending}
                  sx={{ mt: 3 }}
                >
                  {createOrder.isPending ? (
                    <CircularProgress size={24} />
                  ) : (
                    `Place Order - $${cart.total_amount}`
                  )}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Order Summary */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Order Summary
              </Typography>
              <Divider sx={{ my: 2 }} />
              {cart.items.map((item) => (
                <Box
                  key={item.id}
                  display="flex"
                  justifyContent="space-between"
                  mb={1}
                >
                  <Typography variant="body2">
                    {item.product.name} x {item.quantity}
                  </Typography>
                  <Typography variant="body2">${item.subtotal}</Typography>
                </Box>
              ))}
              <Divider sx={{ my: 2 }} />
              <Box display="flex" justifyContent="space-between">
                <Typography variant="h6">Total</Typography>
                <Typography variant="h6">${cart.total_amount}</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}
