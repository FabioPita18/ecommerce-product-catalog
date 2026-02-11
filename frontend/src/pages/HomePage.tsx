/**
 * Home Page
 *
 * The landing page of the application.
 * Displays a hero section and featured products.
 * Full implementation will be completed in Phase 7.
 *
 * Features:
 * - Welcome banner with store description
 * - Grid of featured products fetched from the API
 * - Loading state while products are being fetched
 */
import { Container, Typography, Box, CircularProgress } from '@mui/material';
import Grid from '@mui/material/Grid';
import { useFeaturedProducts } from '@/hooks/useProducts';
import { ProductCard } from '@/components/common/ProductCard';

export function HomePage() {
  const { data: products, isLoading } = useFeaturedProducts();

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box textAlign="center" mb={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome to Our Store
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Discover amazing products at great prices
        </Typography>
      </Box>

      {/* Featured Products */}
      <Typography variant="h4" gutterBottom>
        Featured Products
      </Typography>

      {isLoading ? (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {products?.map((product) => (
            <Grid key={product.id} size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
              <ProductCard product={product} />
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
}
