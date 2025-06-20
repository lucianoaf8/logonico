import { useEffect } from 'react';
import api from '../services/apiService';
import { useAppState } from './useAppState';

let _refresh;
export default function useImages() {
  const { setAllImages } = useAppState();
  _refresh = async ()=>{
    const imgs = await api.getImages();
    setAllImages(imgs);
  };
  useEffect(()=>{ _refresh() }, []);
}
useImages.refresh = ()=>_refresh();
