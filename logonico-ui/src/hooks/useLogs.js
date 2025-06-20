// useLogs.js - Safe version with error handling
import { useEffect } from 'react';
import apiService from '../services/apiService';
import { useAppState } from './useAppState';

let _refresh;
export default function useLogs(intervalMs = 0) {
  const { setLogs } = useAppState();
  
  const parseLine = (line) => {
    const parts = line.split(' | ', 3);
    if (parts.length < 3) return null;
    const [timestamp, _name, rest] = parts; // rest contains LEVEL | message
    const sub = rest.split(' | ', 1);
    const level = sub[0];
    const message = rest.substring(level.length + 3);
    let status = 'ℹ️';
    if (level.includes('ERROR')) status = '❌';
    else if (level.includes('WARNING')) status = '⚠️';
    else if (level.includes('INFO')) status = '✅';
    return {
      time: timestamp.split(' ')[1].slice(0,8),
      status,
      message: message.length>80? message.slice(0,77)+'…' : message
    };
  };
  
  _refresh = async () => {
    try {
      const lg = await apiService.getLogs();
      setLogs(lg || []);
    } catch (error) {
      console.warn('Failed to load logs:', error);
      setLogs([]);
    }
  };
  
  useEffect(() => { 
    _refresh();
    // Open EventSource for live updates
    const es = new EventSource('/api/logs/stream');
    es.onmessage = (e) => {
      if (!e.data) return; // heartbeat
      const logObj = parseLine(e.data);
      if (logObj) {
        setLogs(prev => [...prev.slice(-19), logObj]);
      }
    };
    es.onerror = () => console.warn('Log stream closed');
    return () => es.close();
  }, []);
}
useLogs.refresh = () => _refresh && _refresh();