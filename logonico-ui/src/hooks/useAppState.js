import React, { createContext, useContext, useState } from 'react';

const Ctx = createContext();
export function AppStateProvider({ children }) {
  const [allImages, setAllImages]     = useState([]);
  const [selectedImages, setSelected] = useState(new Set());
  const [stats, setStats]             = useState({});
  const [logs, setLogs]               = useState([]);

  return (
    <Ctx.Provider value={{
      allImages, setAllImages,
      selectedImages, setSelected,
      stats, setStats,
      logs, setLogs
    }}>
      {children}
    </Ctx.Provider>
  );
}
export function useAppState() { return useContext(Ctx); }
