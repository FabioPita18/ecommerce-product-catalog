/**
 * Checkout Page
 *
 * Handles the order creation process.
 * Full implementation with address form and order summary in Phase 7.
 *
 * Current placeholder features:
 * - Shipping address input
 * - Place order button
 * - Redirects to order detail on success
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Paper,
  Alert,
} from '@mui/material';
import { useCreateOrder } from '@/hooks/useOrders';

export function CheckoutPage() {
  const navigate = useNavigate();
  const createOrder = useCreateOrder();
  const [shippingAddress, setShippingAddress] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!shippingAddress.trim()) {
      setError('Please enter a shipping address.');
      return;
    }

    try {
      const order = await createOrder.mutateAsync({
        shipping_address: shippingAddress,
      });
      navigate(`/orders/${order.id}`);
    } catch {
      setError('Failed to create order. Please try again.');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Checkout
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 4 }}>
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="Shipping Address"
            value={shippingAddress}
            onChange={(e) => setShippingAddress(e.target.value)}
            required
            fullWidth
            multiline
            rows={3}
          />
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={createOrder.isPending}
            fullWidth
          >
            {createOrder.isPending ? 'Placing Order...' : 'Place Order'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}
