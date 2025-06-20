import { useEffect } from 'react';
import api from '../services/apiService';
import { useAppState } from './useAppState';

let _refresh;
export default function useLogs() {
  const { setLogs } = useAppState();
  _refresh = async ()=>{
    const lg = await api.getLogs();
    setLogs(lg);
  };
  useEffect(()=>{ _refresh() }, []);
}
useLogs.refresh = ()=>_refresh();
