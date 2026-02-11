/**
 * Order Detail Page
 *
 * Displays full details of a specific order.
 * Full implementation in Phase 7.
 *
 * Current placeholder features:
 * - Order info (status, date, shipping address)
 * - List of order items
 * - Order total
 */
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Paper,
  Chip,
  Divider,
} from '@mui/material';
import { useOrder } from '@/hooks/useOrders';

export function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: order, isLoading, isError } = useOrder(Number(id) || 0);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={8}>
        <CircularProgress />
      </Box>
    );
  }

  if (isError || !order) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography color="error">Order not found.</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Order #{order.id}
        </Typography>
        <Chip label={order.status_display} color="primary" />
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="body2" color="text.secondary">
          Placed on {new Date(order.created_at).toLocaleDateString()}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Shipping to: {order.shipping_address}
        </Typography>
      </Paper>

      {/* Order Items */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Items
        </Typography>
        {order.items.map((item) => (
          <Box key={item.id}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
              <Box>
                <Typography>{item.product.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Qty: {item.quantity} x ${item.price_at_purchase}
                </Typography>
              </Box>
              <Typography fontWeight="bold">${item.subtotal}</Typography>
            </Box>
            <Divider />
          </Box>
        ))}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', pt: 2, mt: 1 }}>
          <Typography variant="h6">Total</Typography>
          <Typography variant="h6" fontWeight="bold">
            ${order.total_amount}
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}
