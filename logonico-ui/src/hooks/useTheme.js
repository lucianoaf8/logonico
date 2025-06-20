import { useState, useEffect } from 'react';

export default function useTheme() {
  const [theme,setTheme] = useState('dark');
  useEffect(()=>{
    document.body.setAttribute('data-theme', theme==='light'?'light':'');
    // swap icon handled in Header
  },[theme]);
  return [theme, ()=>setTheme(t=>t==='light'?'dark':'light')];
}
