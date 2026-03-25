import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import { DashboardPage } from './presentation/pages/DashboardPage.jsx';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <DashboardPage />
  </React.StrictMode>,
);
