// services/themeService.js
/**
 * Theme management service for LogoNico UI
 * Handles dark/light theme switching and persistence
 */

const THEME_STORAGE_KEY = 'logonico-theme';
const THEME_ATTRIBUTE = 'data-theme';

export const THEMES = {
  DARK: 'dark',
  LIGHT: 'light'
};

export const THEME_CONFIG = {
  [THEMES.DARK]: {
    name: 'Dark',
    icon: '🌙',
    colors: {
      'bg-primary': '#0D1117',
      'bg-secondary': '#161B22',
      'bg-tertiary': '#21262D',
      'text-primary': '#F0F6FC',
      'text-secondary': '#8B949E',
      'accent-blue': '#00D9FF',
      'success': '#00D9FF',
      'warning': '#FFC107',
      'error': '#FF5555',
      'processing': '#FF8C00',
      'border': '#30363D',
      'glass-bg': 'rgba(33, 38, 45, 0.8)',
      'glow': '0 0 20px rgba(0, 217, 255, 0.3)',
      'selection': 'rgba(0, 217, 255, 0.2)'
    }
  },
  [THEMES.LIGHT]: {
    name: 'Light',
    icon: '☀️',
    colors: {
      'bg-primary': '#FFFFFF',
      'bg-secondary': '#F6F8FA',
      'bg-tertiary': '#FFFFFF',
      'text-primary': '#24292F',
      'text-secondary': '#656D76',
      'accent-blue': '#00D9FF',
      'success': '#00D9FF',
      'warning': '#FFC107',
      'error': '#FF5555',
      'processing': '#FF8C00',
      'border': '#D0D7DE',
      'glass-bg': 'rgba(246, 248, 250, 0.8)',
      'glow': '0 0 20px rgba(0, 217, 255, 0.2)',
      'selection': 'rgba(0, 217, 255, 0.1)'
    }
  }
};

class ThemeService {
  constructor() {
    this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
    this.listeners = new Set();
    this.initialize();
  }

  initialize() {
    // Apply initial theme
    this.applyTheme(this.currentTheme);
    
    // Listen for system theme changes
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener('change', this.handleSystemThemeChange.bind(this));
    }
  }

  getSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return THEMES.DARK;
    }
    return THEMES.LIGHT;
  }

  getStoredTheme() {
    try {
      return localStorage.getItem(THEME_STORAGE_KEY);
    } catch (error) {
      console.warn('Failed to read theme from localStorage:', error);
      return null;
    }
  }

  setStoredTheme(theme) {
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch (error) {
      console.warn('Failed to save theme to localStorage:', error);
    }
  }

  applyTheme(theme) {
    const config = THEME_CONFIG[theme];
    if (!config) {
      console.warn(`Unknown theme: ${theme}`);
      return;
    }

    // Set theme attribute on document body
    if (theme === THEMES.LIGHT) {
      document.body.setAttribute(THEME_ATTRIBUTE, 'light');
    } else {
      document.body.removeAttribute(THEME_ATTRIBUTE);
    }

    // Apply CSS custom properties
    const root = document.documentElement;
    Object.entries(config.colors).forEach(([property, value]) => {
      root.style.setProperty(`--${property}`, value);
    });

    this.currentTheme = theme;
  }

  setTheme(theme) {
    if (theme === this.currentTheme) return;
    
    this.applyTheme(theme);
    this.setStoredTheme(theme);
    this.notifyListeners(theme);
  }

  toggleTheme() {
    const newTheme = this.currentTheme === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK;
    this.setTheme(newTheme);
    return newTheme;
  }

  getCurrentTheme() {
    return this.currentTheme;
  }

  getCurrentThemeConfig() {
    return THEME_CONFIG[this.currentTheme];
  }

  isCurrentTheme(theme) {
    return this.currentTheme === theme;
  }

  isDarkTheme() {
    return this.currentTheme === THEMES.DARK;
  }

  isLightTheme() {
    return this.currentTheme === THEMES.LIGHT;
  }

  handleSystemThemeChange(e) {
    // Only auto-switch if user hasn't manually set a theme
    if (!this.getStoredTheme()) {
      const systemTheme = e.matches ? THEMES.DARK : THEMES.LIGHT;
      this.setTheme(systemTheme);
    }
  }

  // Event listeners for theme changes
  addListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  removeListener(callback) {
    this.listeners.delete(callback);
  }

  notifyListeners(theme) {
    this.listeners.forEach(callback => {
      try {
        callback(theme);
      } catch (error) {
        console.error('Theme listener error:', error);
      }
    });
  }

  // Utility methods
  getThemeIcon(theme = this.currentTheme) {
    return THEME_CONFIG[theme]?.icon || '🌙';
  }

  getThemeName(theme = this.currentTheme) {
    return THEME_CONFIG[theme]?.name || 'Unknown';
  }

  getAllThemes() {
    return Object.keys(THEME_CONFIG);
  }

  // CSS-in-JS helpers
  getCSSVariable(property) {
    return `var(--${property})`;
  }

  getColorValue(property, theme = this.currentTheme) {
    return THEME_CONFIG[theme]?.colors[property];
  }
}

// Export singleton instance
export const themeService = new ThemeService();

// Export utility functions
export const toggleTheme = () => themeService.toggleTheme();
export const setTheme = (theme) => themeService.setTheme(theme);
export const getCurrentTheme = () => themeService.getCurrentTheme();
export const isDarkTheme = () => themeService.isDarkTheme();
export const isLightTheme = () => themeService.isLightTheme();
export const addThemeListener = (callback) => themeService.addListener(callback);
export const removeThemeListener = (callback) => themeService.removeListener(callback);

export default themeService;