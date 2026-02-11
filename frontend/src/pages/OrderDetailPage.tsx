/**
 * Order Detail Page
 *
 * Displays full details of a specific order.
 *
 * Features:
 * - Order status with color-coded chip
 * - List of order items with prices at time of purchase
 * - Shipping address
 * - Order timestamps (placed/updated)
 * - Cancel button for pending orders
 * - Loading skeleton and error states
 * - Back to orders link
 */
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  Button,
  Divider,
  Skeleton,
  Alert,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { useOrder, useCancelOrder } from '@/hooks/useOrders';
import { useSnackbar } from 'notistack';
import type { OrderStatus } from '@/types';

/** Map order status to MUI Chip color */
const statusColors: Record<
  OrderStatus,
  'default' | 'info' | 'warning' | 'success' | 'error'
> = {
  pending: 'warning',
  processing: 'info',
  shipped: 'info',
  delivered: 'success',
  cancelled: 'error',
};

export function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: order, isLoading, error } = useOrder(Number(id));
  const cancelOrder = useCancelOrder();
  const { enqueueSnackbar } = useSnackbar();

  const handleCancel = async () => {
    if (!order) return;
    if (!confirm('Are you sure you want to cancel this order?')) return;

    try {
      await cancelOrder.mutateAsync(order.id);
      enqueueSnackbar('Order cancelled', { variant: 'success' });
    } catch {
      enqueueSnackbar('Failed to cancel order', { variant: 'error' });
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Skeleton variant="text" width={200} height={40} />
        <Skeleton variant="rectangular" height={300} sx={{ mt: 2 }} />
      </Container>
    );
  }

  if (error || !order) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="error">Order not found.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Header with order number and status */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Typography variant="h4">Order #{order.id}</Typography>
        <Chip
          label={order.status_display}
          color={statusColors[order.status]}
        />
      </Box>

      <Grid container spacing={3}>
        {/* Order Items */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Order Items
              </Typography>
              {order.items.map((item) => (
                <Box key={item.id}>
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    py={2}
                  >
                    <Box>
                      <Typography>{item.product.name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        ${item.price_at_purchase} &times; {item.quantity}
                      </Typography>
                    </Box>
                    <Typography fontWeight="bold">${item.subtotal}</Typography>
                  </Box>
                  <Divider />
                </Box>
              ))}
              <Box display="flex" justifyContent="space-between" mt={2}>
                <Typography variant="h6">Total</Typography>
                <Typography variant="h6">${order.total_amount}</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Sidebar: Shipping + Order Info */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Shipping Address
              </Typography>
              <Typography
                variant="body2"
                style={{ whiteSpace: 'pre-line' }}
              >
                {order.shipping_address}
              </Typography>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Order Info
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Placed: {new Date(order.created_at).toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Updated: {new Date(order.updated_at).toLocaleString()}
              </Typography>

              {/* Cancel button - only for pending orders */}
              {order.status === 'pending' && (
                <Button
                  color="error"
                  fullWidth
                  sx={{ mt: 2 }}
                  onClick={handleCancel}
                  disabled={cancelOrder.isPending}
                >
                  Cancel Order
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Button component={RouterLink} to="/orders" sx={{ mt: 3 }}>
        &larr; Back to Orders
      </Button>
    </Container>
  );
}
