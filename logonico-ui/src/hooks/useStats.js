// useStats.js - Safe version with error handling  
import { useEffect } from 'react';
import apiService from '../services/apiService';
import { useAppState } from './useAppState';

let _refresh;
export default function useStats() {
  const { setStats, allImages } = useAppState();
  
  _refresh = async () => {
    try {
      const s = await apiService.getStats();
      // augment totalSize
      const totalSize = allImages.reduce((a,i) => a + (i.size_mb || 0), 0).toFixed(1);
      setStats({...s, totalSize});
    } catch (error) {
      console.warn('Failed to load stats:', error);
      setStats({ totalSize: '0' }); // Fallback
    }
  };
  
  useEffect(() => { 
    _refresh(); 
  }, [allImages]);
}
useStats.refresh = () => _refresh && _refresh();