import React, { createContext, useContext, useState, useCallback } from 'react';
import { defaultThemes } from '../config/theme.jsx';

const ThemeContext = createContext({
  currentTheme: 'corporate_blue',
  theme: defaultThemes.corporate_blue,
  setTheme: () => {},
  switchTheme: () => {},
  availableThemes: Object.entries(defaultThemes).map(([id, theme]) => ({
    id,
    name: theme.name
  })),
});

export function ThemeProvider({ children }) {
  const [currentTheme, setCurrentTheme] = useState('corporate_blue');
  const [customTheme, setCustomTheme] = useState(null);

  const theme = customTheme || defaultThemes[currentTheme] || defaultThemes.corporate_blue;

  const switchTheme = useCallback((themeId) => {
    if (defaultThemes[themeId]) {
      setCurrentTheme(themeId);
      setCustomTheme(null);
    }
  }, []);

  const setTheme = useCallback((themeConfig) => {
    if (typeof themeConfig === 'object' && themeConfig !== null) {
      setCustomTheme(themeConfig);
    }
  }, []);

  // Apply theme CSS variables whenever theme changes
  React.useEffect(() => {
    if (theme) {
      Object.entries(theme.colors || {}).forEach(([key, value]) => {
        document.documentElement.style.setProperty(`--theme-${key}`, value);
      });
    }
  }, [theme]);

  const value = {
    currentTheme,
    theme,
    setTheme,
    switchTheme,
    availableThemes: Object.entries(defaultThemes).map(([id, themeData]) => ({
      ...themeData,
      id
    })),
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
