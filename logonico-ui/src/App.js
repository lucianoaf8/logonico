import React, { useEffect } from 'react';
import { AppStateProvider } from './hooks/useAppState';
import useImages from './hooks/useImages';
import useStats from './hooks/useStats';
import useLogs from './hooks/useLogs';
import useTheme from './hooks/useTheme';
import AppLayout from './components/Layout/AppLayout';
import './App.css';

// Inner component that uses the context hooks
function AppContent() {
  const [theme, toggleTheme] = useTheme();
  
  // Initialize data hooks (these need to be inside AppStateProvider)
  useImages();
  useStats();
  useLogs();

  useEffect(() => {
    // Refresh data every 30 seconds
    const interval = setInterval(() => {
      useImages.refresh();
      useStats.refresh();
      useLogs.refresh();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div data-theme={theme === 'light' ? 'light' : ''}>
      <AppLayout onToggleTheme={toggleTheme} />
    </div>
  );
}

// Main App component that provides context
export default function App() {
  return (
    <AppStateProvider>
      <AppContent />
    </AppStateProvider>
  );
}