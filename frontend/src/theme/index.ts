/**
 * Material-UI Custom Theme
 *
 * Centralizes the visual design of the application.
 * MUI's theming system lets us customize colors, typography, spacing,
 * and component defaults in one place.
 *
 * Theme structure:
 * - palette: Color scheme (primary, secondary, error, background, etc.)
 * - typography: Font family, sizes, weights for each variant (h1-h6, body, etc.)
 * - shape: Border radius defaults
 * - components: Default props and style overrides for specific MUI components
 *
 * MUI Theming docs: https://mui.com/material-ui/customization/theming/
 */
import { createTheme } from '@mui/material/styles';
import type { ThemeOptions } from '@mui/material/styles';

const themeOptions: ThemeOptions = {
  palette: {
    primary: {
      main: '#1976d2', // MUI default blue
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#fff',
    },
    secondary: {
      main: '#9c27b0', // Purple for accents (featured badges, etc.)
      light: '#ba68c8',
      dark: '#7b1fa2',
      contrastText: '#fff',
    },
    error: {
      main: '#d32f2f',
    },
    warning: {
      main: '#ed6c02',
    },
    success: {
      main: '#2e7d32',
    },
    background: {
      default: '#f5f5f5', // Light gray page background
      paper: '#ffffff', // White card/surface background
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2.5rem', fontWeight: 500 },
    h2: { fontSize: '2rem', fontWeight: 500 },
    h3: { fontSize: '1.75rem', fontWeight: 500 },
    h4: { fontSize: '1.5rem', fontWeight: 500 },
    h5: { fontSize: '1.25rem', fontWeight: 500 },
    h6: { fontSize: '1rem', fontWeight: 500 },
  },
  shape: {
    borderRadius: 8, // Slightly rounded corners on all components
  },
  components: {
    // Remove uppercase text transform from buttons (more modern look)
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
      defaultProps: {
        disableElevation: true, // Flat buttons by default
      },
    },
    // Subtle shadow on cards
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
    // Default text field variant and size
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
        size: 'small',
      },
    },
  },
};

export const theme = createTheme(themeOptions);
