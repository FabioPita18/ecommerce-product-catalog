/**
 * Shopping Cart Page
 *
 * Displays the user's cart with full item management capabilities.
 *
 * Features:
 * - Cart item list with product image, name, price
 * - Quantity controls (+/- buttons and direct input)
 * - Remove individual items
 * - Clear entire cart
 * - Order summary sidebar with totals
 * - Empty cart state with "Continue Shopping" link
 * - Loading and error states
 *
 * All cart mutations use TanStack Query hooks that automatically
 * invalidate the cart cache to keep the UI in sync.
 */
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Card,
  CardContent,
  CardMedia,
  Box,
  Button,
  IconButton,
  TextField,
  Divider,
  Skeleton,
  Alert,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import {
  useCart,
  useUpdateCartItem,
  useRemoveCartItem,
  useClearCart,
} from '@/hooks/useCart';
import { useSnackbar } from 'notistack';

export function CartPage() {
  const { data: cart, isLoading, error } = useCart();
  const updateItem = useUpdateCartItem();
  const removeItem = useRemoveCartItem();
  const clearCart = useClearCart();
  const { enqueueSnackbar } = useSnackbar();

  const handleQuantityChange = async (
    itemId: number,
    newQuantity: number
  ) => {
    if (newQuantity < 1) return;
    try {
      await updateItem.mutateAsync({ itemId, quantity: newQuantity });
    } catch {
      enqueueSnackbar('Failed to update quantity', { variant: 'error' });
    }
  };

  const handleRemoveItem = async (itemId: number) => {
    try {
      await removeItem.mutateAsync(itemId);
      enqueueSnackbar('Item removed from cart', { variant: 'success' });
    } catch {
      enqueueSnackbar('Failed to remove item', { variant: 'error' });
    }
  };

  const handleClearCart = async () => {
    try {
      await clearCart.mutateAsync();
      enqueueSnackbar('Cart cleared', { variant: 'success' });
    } catch {
      enqueueSnackbar('Failed to clear cart', { variant: 'error' });
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Skeleton variant="text" width={200} height={40} />
        {[1, 2, 3].map((i) => (
          <Skeleton
            key={i}
            variant="rectangular"
            height={150}
            sx={{ mb: 2 }}
          />
        ))}
      </Container>
    );
  }

  // Error state
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">Failed to load cart. Please try again.</Alert>
      </Container>
    );
  }

  // Empty cart state
  if (!cart || cart.items.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Shopping Cart
        </Typography>
        <Card sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Your cart is empty
          </Typography>
          <Button
            variant="contained"
            component={RouterLink}
            to="/products"
            sx={{ mt: 2 }}
          >
            Continue Shopping
          </Button>
        </Card>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Typography variant="h4">Shopping Cart</Typography>
        <Button
          color="error"
          onClick={handleClearCart}
          disabled={clearCart.isPending}
        >
          Clear Cart
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Cart Items */}
        <Grid size={{ xs: 12, md: 8 }}>
          {cart.items.map((item) => (
            <Card key={item.id} sx={{ mb: 2 }}>
              <CardContent>
                <Grid container spacing={2} sx={{ alignItems: 'center' }}>
                  {/* Product Image */}
                  <Grid size={{ xs: 3, sm: 2 }}>
                    <CardMedia
                      component="img"
                      image={item.product.image || '/placeholder.png'}
                      alt={item.product.name}
                      sx={{ borderRadius: 1, aspectRatio: '1' }}
                    />
                  </Grid>
                  {/* Product Name & Price */}
                  <Grid size={{ xs: 9, sm: 4 }}>
                    <Typography
                      variant="subtitle1"
                      component={RouterLink}
                      to={`/products/${item.product.slug}`}
                      sx={{ textDecoration: 'none', color: 'inherit' }}
                    >
                      {item.product.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      ${item.product.price} each
                    </Typography>
                  </Grid>
                  {/* Quantity Controls */}
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Box display="flex" alignItems="center">
                      <IconButton
                        size="small"
                        onClick={() =>
                          handleQuantityChange(item.id, item.quantity - 1)
                        }
                        disabled={item.quantity <= 1}
                      >
                        <RemoveIcon />
                      </IconButton>
                      <TextField
                        value={item.quantity}
                        size="small"
                        sx={{ width: 60, mx: 1 }}
                        slotProps={{
                          htmlInput: { style: { textAlign: 'center' } },
                        }}
                        onChange={(e) => {
                          const val = parseInt(e.target.value);
                          if (!isNaN(val))
                            handleQuantityChange(item.id, val);
                        }}
                      />
                      <IconButton
                        size="small"
                        onClick={() =>
                          handleQuantityChange(item.id, item.quantity + 1)
                        }
                      >
                        <AddIcon />
                      </IconButton>
                    </Box>
                  </Grid>
                  {/* Subtotal */}
                  <Grid size={{ xs: 4, sm: 2 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      ${item.subtotal}
                    </Typography>
                  </Grid>
                  {/* Remove Button */}
                  <Grid size={{ xs: 2, sm: 1 }}>
                    <IconButton
                      color="error"
                      onClick={() => handleRemoveItem(item.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          ))}
        </Grid>

        {/* Order Summary Sidebar */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Order Summary
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography>Items ({cart.total_items})</Typography>
                <Typography>${cart.total_amount}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography>Shipping</Typography>
                <Typography color="success.main">Free</Typography>
              </Box>
              <Divider sx={{ my: 2 }} />
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography variant="h6">Total</Typography>
                <Typography variant="h6">${cart.total_amount}</Typography>
              </Box>
              <Button
                variant="contained"
                fullWidth
                size="large"
                component={RouterLink}
                to="/checkout"
              >
                Proceed to Checkout
              </Button>
              <Button
                variant="text"
                fullWidth
                component={RouterLink}
                to="/products"
                sx={{ mt: 1 }}
              >
                Continue Shopping
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}
