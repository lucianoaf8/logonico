import { useState, useEffect } from 'react';

export default function useTheme() {
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('logonico-theme') || 'dark';
    setTheme(savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('logonico-theme', newTheme);
  };

  return [theme, toggleTheme];
}