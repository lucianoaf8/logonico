import React, { createContext, useContext, useState } from 'react';

const AppStateContext = createContext();

export function AppStateProvider({ children }) {
  const [allImages, setAllImages] = useState([]);
  const [selectedImages, setSelectedImages] = useState(new Set());
  const [stats, setStats] = useState({});
  const [logs, setLogs] = useState([]);

  return (
    <AppStateContext.Provider value={{
      allImages, setAllImages,
      selectedImages, setSelectedImages,
      stats, setStats,
      logs, setLogs
    }}>
      {children}
    </AppStateContext.Provider>
  );
}

export function useAppState() { 
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error('useAppState must be used within AppStateProvider');
  }
  return context;
}