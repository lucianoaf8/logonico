import React, { useEffect } from 'react';
import { AppStateProvider } from './hooks/useAppState';
import useImages from './hooks/useImages';
import useStats from './hooks/useStats';
import useLogs from './hooks/useLogs';
import useTheme from './hooks/useTheme';
import AppLayout from './components/Layout/AppLayout';

export default function App() {
  const [theme, toggleTheme] = useTheme();
  // initialize data
  useImages();
  useStats();
  useLogs();

  useEffect(() => {
    const iv = setInterval(() => {
      useImages.refresh();
      useStats.refresh();
      useLogs.refresh();
    }, 30_000);
    return ()=>clearInterval(iv);
  }, []);

  return (
    <AppStateProvider>
      <div data-theme={theme==='light'?'light':''}>
        <AppLayout onToggleTheme={toggleTheme}/>
      </div>
    </AppStateProvider>
  );
}
