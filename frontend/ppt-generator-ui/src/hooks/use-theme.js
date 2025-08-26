import { useState, useEffect, useCallback } from 'react';
import { defaultThemes, defaultAnimations, defaultLayouts } from '../config/theme.jsx';

export const useTheme = (initialTheme = 'modern') => {
  const [currentTheme, setCurrentTheme] = useState(initialTheme);
  const [customTheme, setCustomTheme] = useState(null);

  const theme = customTheme || defaultThemes[currentTheme];

  const switchTheme = useCallback((themeName) => {
    if (defaultThemes[themeName]) {
      setCurrentTheme(themeName);
      setCustomTheme(null);
    }
  }, []);

  const updateCustomTheme = useCallback((themeUpdates) => {
    setCustomTheme(prev => ({
      ...(prev || defaultThemes[currentTheme]),
      ...themeUpdates
    }));
  }, [currentTheme]);

  const getThemeValue = useCallback((path) => {
    const parts = path.split('.');
    let value = theme;
    
    for (const part of parts) {
      if (value === undefined) break;
      value = value[part];
    }
    
    return value;
  }, [theme]);

  const getAnimation = useCallback((name) => {
    return defaultAnimations[name] || defaultAnimations.fadeIn;
  }, []);

  const getLayout = useCallback((type) => {
    return defaultLayouts[type] || defaultLayouts.content;
  }, []);

  return {
    theme,
    currentTheme,
    switchTheme,
    updateCustomTheme,
    getThemeValue,
    getAnimation,
    getLayout,
    availableThemes: Object.keys(defaultThemes),
    animations: defaultAnimations,
    layouts: defaultLayouts
  };
};
