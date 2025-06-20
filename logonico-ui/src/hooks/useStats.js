import { useEffect } from 'react';
import api from '../services/apiService';
import { useAppState } from './useAppState';

let _refresh;
export default function useStats() {
  const { setStats, allImages } = useAppState();
  _refresh = async ()=>{
    const s = await api.getStats();
    // augment totalSize
    s.totalSize = allImages.reduce((a,i)=>a+i.size_mb,0).toFixed(1);
    setStats(s);
  };
  useEffect(()=>{ _refresh() }, [allImages]);
}
useStats.refresh = ()=>_refresh();
