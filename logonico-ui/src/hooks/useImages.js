// useImages.js - Safe version with error handling
import { useEffect } from 'react';
import apiService from '../services/apiService';
import { useAppState } from './useAppState';

let _refresh;
export default function useImages() {
  const { setAllImages } = useAppState();
  
  _refresh = async () => {
    try {
      const imgs = await apiService.getImages();
      setAllImages(imgs || []); // Fallback to empty array
    } catch (error) {
      console.warn('Failed to load images:', error);
      setAllImages([]); // Fallback to empty array
    }
  };
  
  useEffect(() => { 
    _refresh(); 
  }, []);
}
useImages.refresh = () => _refresh && _refresh();