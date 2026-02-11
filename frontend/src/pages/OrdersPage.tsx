/**
 * Orders List Page
 *
 * Displays the user's order history with status badges.
 *
 * Features:
 * - List of all orders with status, total, date, item count
 * - Color-coded status chips (pending=warning, delivered=success, etc.)
 * - Link to order detail page
 * - Empty state with "Start Shopping" link
 * - Loading skeleton and error states
 */
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  Button,
  Skeleton,
  Alert,
} from '@mui/material';
import { useOrders } from '@/hooks/useOrders';
import type { OrderStatus } from '@/types';

/**
 * Map order status to MUI Chip color.
 * Makes it easy to visually identify order states at a glance.
 */
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

export function OrdersPage() {
  const { data: orders, isLoading, error } = useOrders();

  if (isLoading) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          My Orders
        </Typography>
        {[1, 2, 3].map((i) => (
          <Skeleton
            key={i}
            variant="rectangular"
            height={100}
            sx={{ mb: 2 }}
          />
        ))}
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="error">Failed to load orders.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        My Orders
      </Typography>

      {orders?.length === 0 ? (
        <Card sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary" gutterBottom>
            You haven&apos;t placed any orders yet.
          </Typography>
          <Button
            variant="contained"
            component={RouterLink}
            to="/products"
            sx={{ mt: 2 }}
          >
            Start Shopping
          </Button>
        </Card>
      ) : (
        orders?.map((order) => (
          <Card key={order.id} sx={{ mb: 2 }}>
            <CardContent>
              <Box
                display="flex"
                justifyContent="space-between"
                alignItems="center"
              >
                <Box>
                  <Typography variant="h6">Order #{order.id}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {new Date(order.created_at).toLocaleDateString()} &middot;{' '}
                    {order.item_count} item{order.item_count !== 1 ? 's' : ''}
                  </Typography>
                </Box>
                <Box textAlign="right">
                  <Chip
                    label={order.status_display}
                    color={statusColors[order.status]}
                    size="small"
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="h6">${order.total_amount}</Typography>
                </Box>
              </Box>
              <Button
                component={RouterLink}
                to={`/orders/${order.id}`}
                sx={{ mt: 2 }}
              >
                View Details
              </Button>
            </CardContent>
          </Card>
        ))
      )}
    </Container>
  );
}
