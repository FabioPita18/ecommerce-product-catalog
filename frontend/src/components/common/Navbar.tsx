/**
 * Navigation Bar Component
 *
 * The main navigation bar displayed at the top of every page.
 *
 * Features:
 * - Logo/brand name linking to home
 * - Products page link
 * - Cart icon with item count badge (authenticated users)
 * - User dropdown menu with profile/orders/logout (authenticated users)
 * - Login/Register buttons (unauthenticated users)
 *
 * Uses MUI's AppBar component for Material Design styling.
 * The "sticky" position keeps the navbar visible while scrolling.
 *
 * MUI AppBar docs: https://mui.com/material-ui/react-app-bar/
 */
import { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Box,
  Container,
} from '@mui/material';
import {
  ShoppingCart as CartIcon,
  AccountCircle as AccountIcon,
  Store as StoreIcon,
} from '@mui/icons-material';
import { useAuth } from '@/contexts/AuthContext';
import { useCartSummary } from '@/hooks/useCart';

export function Navbar() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const { data: cartSummary } = useCartSummary();

  // Anchor element for the user dropdown menu
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleMenuClose();
    await logout();
    navigate('/');
  };

  return (
    <AppBar position="sticky">
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          {/* Brand Logo */}
          <StoreIcon sx={{ mr: 1 }} />
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              flexGrow: 1,
              textDecoration: 'none',
              color: 'inherit',
              fontWeight: 700,
            }}
          >
            E-Commerce Store
          </Typography>

          {/* Navigation Links */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Button
              color="inherit"
              component={RouterLink}
              to="/products"
            >
              Products
            </Button>

            {isAuthenticated ? (
              <>
                {/* Cart Icon with Badge */}
                <IconButton
                  color="inherit"
                  component={RouterLink}
                  to="/cart"
                >
                  <Badge
                    badgeContent={cartSummary?.total_items || 0}
                    color="secondary"
                  >
                    <CartIcon />
                  </Badge>
                </IconButton>

                {/* User Account Menu */}
                <IconButton color="inherit" onClick={handleMenuOpen}>
                  <AccountIcon />
                </IconButton>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                >
                  {/* Show user name (disabled = non-clickable header) */}
                  <MenuItem disabled>
                    {user?.first_name} {user?.last_name}
                  </MenuItem>
                  <MenuItem
                    component={RouterLink}
                    to="/orders"
                    onClick={handleMenuClose}
                  >
                    My Orders
                  </MenuItem>
                  <MenuItem onClick={handleLogout}>Logout</MenuItem>
                </Menu>
              </>
            ) : (
              <>
                {/* Auth Buttons for Unauthenticated Users */}
                <Button
                  color="inherit"
                  component={RouterLink}
                  to="/login"
                >
                  Login
                </Button>
                <Button
                  color="inherit"
                  variant="outlined"
                  component={RouterLink}
                  to="/register"
                  sx={{ borderColor: 'white' }}
                >
                  Register
                </Button>
              </>
            )}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
