/**
 * Products Listing Page
 *
 * Displays a paginated, filterable grid of all products.
 *
 * Features:
 * - Category filter dropdown
 * - Text search
 * - Price range slider
 * - In-stock only checkbox
 * - Sort by price/name/newest
 * - Pagination
 * - Responsive: filters in sidebar on desktop, drawer on mobile
 * - URL-synced filters (shareable filtered URLs)
 *
 * Filter state is stored in URL search params so users can bookmark
 * or share filtered views. The useSearchParams hook from React Router
 * keeps the URL and filter state in sync.
 *
 * MUI Grid (v7): Uses `size` prop instead of `item xs` props.
 */
import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  TextField,
  Pagination,
  Skeleton,
  Card,
  CardContent,
  Drawer,
  Button,
  Slider,
  Checkbox,
  FormControlLabel,
  IconButton,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
import Grid from '@mui/material/Grid';
import MenuItem from '@mui/material/MenuItem';
import { FilterList as FilterIcon } from '@mui/icons-material';
import { useProducts, useCategories } from '@/hooks/useProducts';
import { ProductCard } from '@/components/common/ProductCard';
import type { ProductFilters } from '@/types';

export function ProductsPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [searchParams, setSearchParams] = useSearchParams();
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Derive filter state from URL search params
  const filters: ProductFilters = {
    category: searchParams.get('category') || undefined,
    search: searchParams.get('search') || undefined,
    min_price: searchParams.get('min_price')
      ? Number(searchParams.get('min_price'))
      : undefined,
    max_price: searchParams.get('max_price')
      ? Number(searchParams.get('max_price'))
      : undefined,
    in_stock: searchParams.get('in_stock') === 'true' ? true : undefined,
    ordering: searchParams.get('ordering') || undefined,
    page: searchParams.get('page') ? Number(searchParams.get('page')) : 1,
  };

  const { data, isLoading } = useProducts(filters);
  const { data: categories } = useCategories();

  /**
   * Update a single filter value in the URL.
   * Resets to page 1 when any non-page filter changes.
   */
  const updateFilter = (
    key: string,
    value: string | number | boolean | null
  ) => {
    const newParams = new URLSearchParams(searchParams);
    if (value === null || value === '' || value === false) {
      newParams.delete(key);
    } else {
      newParams.set(key, String(value));
    }
    // Reset to page 1 when filters change (not when changing page itself)
    if (key !== 'page') {
      newParams.delete('page');
    }
    setSearchParams(newParams);
  };

  const totalPages = data ? Math.ceil(data.count / 12) : 0;

  /** Filter panel content - reused in both sidebar and mobile drawer */
  const FilterContent = () => (
    <Box sx={{ p: 2, width: isMobile ? 280 : '100%' }}>
      <Typography variant="h6" gutterBottom>
        Filters
      </Typography>

      {/* Category Filter */}
      <FormControl fullWidth margin="normal" size="small">
        <InputLabel>Category</InputLabel>
        <Select
          value={filters.category || ''}
          label="Category"
          onChange={(e: SelectChangeEvent) =>
            updateFilter('category', e.target.value || null)
          }
        >
          <MenuItem value="">All Categories</MenuItem>
          {categories?.map((cat) => (
            <MenuItem key={cat.id} value={cat.slug}>
              {cat.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* Text Search */}
      <TextField
        fullWidth
        margin="normal"
        size="small"
        label="Search"
        value={filters.search || ''}
        onChange={(e) => updateFilter('search', e.target.value || null)}
      />

      {/* Price Range Slider */}
      <Typography gutterBottom sx={{ mt: 2 }}>
        Price Range
      </Typography>
      <Slider
        value={[filters.min_price || 0, filters.max_price || 1000]}
        onChange={(_event, newValue) => {
          const [min, max] = newValue as number[];
          updateFilter('min_price', min > 0 ? min : null);
          updateFilter('max_price', max < 1000 ? max : null);
        }}
        valueLabelDisplay="auto"
        min={0}
        max={1000}
        marks={[
          { value: 0, label: '$0' },
          { value: 500, label: '$500' },
          { value: 1000, label: '$1000' },
        ]}
      />

      {/* In Stock Only */}
      <FormControlLabel
        control={
          <Checkbox
            checked={filters.in_stock || false}
            onChange={(e) =>
              updateFilter('in_stock', e.target.checked || null)
            }
          />
        }
        label="In Stock Only"
      />
    </Box>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header with title and sort control */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Typography variant="h4" component="h1">
          Products
        </Typography>

        <Box display="flex" gap={2} alignItems="center">
          {/* Mobile filter toggle */}
          {isMobile && (
            <IconButton onClick={() => setDrawerOpen(true)}>
              <FilterIcon />
            </IconButton>
          )}

          {/* Sort dropdown */}
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Sort By</InputLabel>
            <Select
              value={filters.ordering || ''}
              label="Sort By"
              onChange={(e: SelectChangeEvent) =>
                updateFilter('ordering', e.target.value || null)
              }
            >
              <MenuItem value="">Default</MenuItem>
              <MenuItem value="price">Price: Low to High</MenuItem>
              <MenuItem value="-price">Price: High to Low</MenuItem>
              <MenuItem value="-created_at">Newest</MenuItem>
              <MenuItem value="name">Name A-Z</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Desktop Filter Sidebar */}
        {!isMobile && (
          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent>
                <FilterContent />
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Product Grid */}
        <Grid size={{ xs: 12, md: isMobile ? 12 : 9 }}>
          {isLoading ? (
            // Loading skeleton grid
            <Grid container spacing={3}>
              {[...Array(8)].map((_, i) => (
                <Grid key={i} size={{ xs: 12, sm: 6, lg: 4 }}>
                  <Skeleton variant="rectangular" height={300} />
                </Grid>
              ))}
            </Grid>
          ) : data?.results.length === 0 ? (
            <Typography textAlign="center" color="text.secondary" py={4}>
              No products found matching your criteria.
            </Typography>
          ) : (
            <>
              <Grid container spacing={3}>
                {data?.results.map((product) => (
                  <Grid key={product.id} size={{ xs: 12, sm: 6, lg: 4 }}>
                    <ProductCard product={product} />
                  </Grid>
                ))}
              </Grid>

              {/* Pagination */}
              {totalPages > 1 && (
                <Box display="flex" justifyContent="center" mt={4}>
                  <Pagination
                    count={totalPages}
                    page={filters.page || 1}
                    onChange={(_event, page) => updateFilter('page', page)}
                    color="primary"
                  />
                </Box>
              )}
            </>
          )}
        </Grid>
      </Grid>

      {/* Mobile Filters Drawer */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <FilterContent />
        <Button
          variant="contained"
          sx={{ m: 2 }}
          onClick={() => setDrawerOpen(false)}
        >
          Apply Filters
        </Button>
      </Drawer>
    </Container>
  );
}
