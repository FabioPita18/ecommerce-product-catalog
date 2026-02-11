/**
 * Cart Page
 *
 * Displays the user's shopping cart with items, quantities, and totals.
 * Full implementation with quantity controls and checkout flow in Phase 7.
 *
 * Current placeholder features:
 * - List of cart items with product info
 * - Cart total
 * - Checkout button
 */
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  CircularProgress,
  Paper,
} from '@mui/material';
import { useCart } from '@/hooks/useCart';

export function CartPage() {
  const { data: cart, isLoading } = useCart();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={8}>
        <CircularProgress />
      </Box>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Shopping Cart
        </Typography>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Your cart is empty
          </Typography>
          <Button
            variant="contained"
            component={RouterLink}
            to="/products"
          >
            Browse Products
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Shopping Cart ({cart.total_items} items)
      </Typography>

      {/* Cart Items - full implementation in Phase 7 */}
      {cart.items.map((item) => (
        <Paper key={item.id} sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h6">{item.product.name}</Typography>
              <Typography color="text.secondary">
                Qty: {item.quantity} x ${item.product.price}
              </Typography>
            </Box>
            <Typography variant="h6">${item.subtotal}</Typography>
          </Box>
        </Paper>
      ))}

      {/* Cart Total */}
      <Paper sx={{ p: 2, mt: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5">Total</Typography>
          <Typography variant="h5" fontWeight="bold">
            ${cart.total_amount}
          </Typography>
        </Box>
        <Button
          variant="contained"
          size="large"
          fullWidth
          component={RouterLink}
          to="/checkout"
          sx={{ mt: 2 }}
        >
          Proceed to Checkout
        </Button>
      </Paper>
    </Container>
  );
}
