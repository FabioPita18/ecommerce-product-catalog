/**
 * Products Page
 *
 * Displays a paginated, filterable grid of all products.
 * Full filtering/pagination UI will be completed in Phase 7.
 *
 * Current placeholder features:
 * - Product grid using ProductCard components
 * - Loading and error states
 */
import { Container, Typography, Box, CircularProgress } from '@mui/material';
import Grid from '@mui/material/Grid';
import { useProducts } from '@/hooks/useProducts';
import { ProductCard } from '@/components/common/ProductCard';

export function ProductsPage() {
  const { data, isLoading, isError, error } = useProducts();

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Products
      </Typography>

      {isLoading ? (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      ) : isError ? (
        <Typography color="error">
          Error loading products: {error?.message}
        </Typography>
      ) : (
        <Grid container spacing={3}>
          {data?.results.map((product) => (
            <Grid key={product.id} size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
              <ProductCard product={product} />
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
}
