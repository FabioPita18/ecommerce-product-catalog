/**
 * Product Card Component
 *
 * Displays a product in a card format for grid/list views.
 *
 * Features:
 * - Product image with gray placeholder if no image
 * - Category chip and "Featured" badge
 * - Product name linking to detail page
 * - Price display
 * - "Add to Cart" button with loading state
 * - Stock status indicator
 *
 * The card uses MUI's Card component with a flexbox layout
 * so the button stays at the bottom regardless of content height.
 *
 * MUI Card docs: https://mui.com/material-ui/react-card/
 */
import { Link as RouterLink } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
} from '@mui/material';
import { ShoppingCart as CartIcon } from '@mui/icons-material';
import { useAuth } from '@/contexts/AuthContext';
import { useAddToCart } from '@/hooks/useCart';
import { useSnackbar } from 'notistack';
import type { ProductListItem } from '@/types';

interface ProductCardProps {
  product: ProductListItem;
}

export function ProductCard({ product }: ProductCardProps) {
  const { isAuthenticated } = useAuth();
  const addToCart = useAddToCart();
  const { enqueueSnackbar } = useSnackbar();

  const handleAddToCart = async () => {
    try {
      await addToCart.mutateAsync({ product_id: product.id, quantity: 1 });
      enqueueSnackbar('Added to cart!', { variant: 'success' });
    } catch {
      enqueueSnackbar('Failed to add to cart', { variant: 'error' });
    }
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Product Image */}
      <CardMedia
        component={RouterLink}
        to={`/products/${product.slug}`}
        sx={{
          height: 200,
          backgroundColor: 'grey.200',
          backgroundImage: product.image ? `url(${product.image})` : 'none',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          display: 'block',
        }}
      />

      {/* Card Content */}
      <CardContent sx={{ flexGrow: 1 }}>
        {/* Category + Featured Badges */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Chip
            label={product.category.name}
            size="small"
            color="primary"
            variant="outlined"
          />
          {product.featured && (
            <Chip label="Featured" size="small" color="secondary" />
          )}
        </Box>

        {/* Product Name (links to detail page) */}
        <Typography
          gutterBottom
          variant="h6"
          component={RouterLink}
          to={`/products/${product.slug}`}
          sx={{ textDecoration: 'none', color: 'inherit', display: 'block' }}
        >
          {product.name}
        </Typography>

        {/* Price */}
        <Typography variant="h5" color="primary" fontWeight="bold">
          ${product.price}
        </Typography>

        {/* Out of Stock Warning */}
        {!product.is_in_stock && (
          <Typography variant="body2" color="error">
            Out of Stock
          </Typography>
        )}
      </CardContent>

      {/* Add to Cart Button */}
      <CardActions>
        <Button
          fullWidth
          variant="contained"
          startIcon={<CartIcon />}
          onClick={handleAddToCart}
          disabled={
            !product.is_in_stock || !isAuthenticated || addToCart.isPending
          }
        >
          {!isAuthenticated
            ? 'Login to Add'
            : addToCart.isPending
              ? 'Adding...'
              : 'Add to Cart'}
        </Button>
      </CardActions>
    </Card>
  );
}
