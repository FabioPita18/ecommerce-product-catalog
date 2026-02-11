/**
 * Orders Page
 *
 * Displays the user's order history.
 * Full implementation with filtering and sorting in Phase 7.
 *
 * Current placeholder features:
 * - List of orders with status, total, and date
 * - Links to order detail pages
 */
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Paper,
  Chip,
  Button,
} from '@mui/material';
import { useOrders } from '@/hooks/useOrders';

export function OrdersPage() {
  const { data: orders, isLoading, isError } = useOrders();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={8}>
        <CircularProgress />
      </Box>
    );
  }

  if (isError) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography color="error">Error loading orders.</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        My Orders
      </Typography>

      {!orders || orders.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No orders yet
          </Typography>
          <Button variant="contained" component={RouterLink} to="/products">
            Start Shopping
          </Button>
        </Paper>
      ) : (
        orders.map((order) => (
          <Paper key={order.id} sx={{ p: 2, mb: 2 }}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <Box>
                <Typography variant="h6">Order #{order.id}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {new Date(order.created_at).toLocaleDateString()} &middot;{' '}
                  {order.item_count} item{order.item_count !== 1 ? 's' : ''}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Chip label={order.status_display} size="small" />
                <Typography variant="h6" fontWeight="bold">
                  ${order.total_amount}
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  component={RouterLink}
                  to={`/orders/${order.id}`}
                >
                  View Details
                </Button>
              </Box>
            </Box>
          </Paper>
        ))
      )}
    </Container>
  );
}
