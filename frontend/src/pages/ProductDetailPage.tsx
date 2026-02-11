/**
 * Product Detail Page
 *
 * Displays full details of a single product.
 * Full implementation will be completed in Phase 7.
 *
 * Current placeholder features:
 * - Fetches product by slug from URL params
 * - Shows product name, description, price, stock status
 * - Add to cart button
 */
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Button,
  Chip,
} from '@mui/material';
import { ShoppingCart as CartIcon } from '@mui/icons-material';
import { useProduct } from '@/hooks/useProducts';
import { useAddToCart } from '@/hooks/useCart';
import { useAuth } from '@/hooks/useAuth';
import { useSnackbar } from 'notistack';

export function ProductDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: product, isLoading, isError } = useProduct(slug || '');
  const { isAuthenticated } = useAuth();
  const addToCart = useAddToCart();
  const { enqueueSnackbar } = useSnackbar();

  const handleAddToCart = async () => {
    if (!product) return;
    try {
      await addToCart.mutateAsync({ product_id: product.id, quantity: 1 });
      enqueueSnackbar('Added to cart!', { variant: 'success' });
    } catch {
      enqueueSnackbar('Failed to add to cart', { variant: 'error' });
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={8}>
        <CircularProgress />
      </Box>
    );
  }

  if (isError || !product) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography color="error">Product not found.</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
        {/* Product Image */}
        <Box
          sx={{
            width: { xs: '100%', md: 400 },
            height: 400,
            backgroundColor: 'grey.200',
            backgroundImage: product.image ? `url(${product.image})` : 'none',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            borderRadius: 2,
          }}
        />

        {/* Product Info */}
        <Box sx={{ flex: 1, minWidth: 300 }}>
          <Chip
            label={product.category.name}
            color="primary"
            variant="outlined"
            sx={{ mb: 2 }}
          />
          {product.featured && (
            <Chip label="Featured" color="secondary" sx={{ mb: 2, ml: 1 }} />
          )}

          <Typography variant="h3" component="h1" gutterBottom>
            {product.name}
          </Typography>

          <Typography variant="h4" color="primary" fontWeight="bold" gutterBottom>
            ${product.price}
          </Typography>

          <Typography
            variant="body1"
            color={product.is_in_stock ? 'success.main' : 'error.main'}
            gutterBottom
          >
            {product.is_in_stock
              ? `In Stock (${product.inventory_count} available)`
              : 'Out of Stock'}
          </Typography>

          <Typography variant="body1" sx={{ my: 2 }}>
            {product.description}
          </Typography>

          <Button
            variant="contained"
            size="large"
            startIcon={<CartIcon />}
            onClick={handleAddToCart}
            disabled={
              !product.is_in_stock || !isAuthenticated || addToCart.isPending
            }
          >
            {!isAuthenticated
              ? 'Login to Add to Cart'
              : addToCart.isPending
                ? 'Adding...'
                : 'Add to Cart'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
}
