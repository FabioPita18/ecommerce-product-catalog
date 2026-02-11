/**
 * Application Entry Point
 *
 * This is the first file that runs when the app loads.
 * It mounts the React application to the #root DOM element.
 *
 * StrictMode enables additional development warnings:
 * - Detects unsafe lifecycle methods
 * - Warns about legacy string refs
 * - Detects unexpected side effects (renders components twice in dev)
 *
 * React StrictMode: https://react.dev/reference/react/StrictMode
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
