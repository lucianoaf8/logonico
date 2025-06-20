// useLogs.js - Safe version with error handling
import { useEffect } from 'react';
import apiService from '../services/apiService';
import { useAppState } from './useAppState';

let _refresh;
export default function useLogs() {
  const { setLogs } = useAppState();
  
  _refresh = async () => {
    try {
      const lg = await apiService.getLogs();
      setLogs(lg || []); // Fallback to empty array
    } catch (error) {
      console.warn('Failed to load logs:', error);
      setLogs([]); // Fallback to empty array
    }
  };
  
  useEffect(() => { 
    _refresh(); 
  }, []);
}
useLogs.refresh = () => _refresh && _refresh();