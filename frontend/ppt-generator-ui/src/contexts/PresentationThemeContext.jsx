import React, { createContext, useContext, useState } from 'react';

const PresentationThemeContext = createContext();

export const themes = {
  modern: {
    name: 'Modern',
    colors: {
      primary: 'rgb(37, 99, 235)',
      secondary: 'rgb(79, 70, 229)',
      accent: 'rgb(236, 72, 153)',
      background: 'rgb(249, 250, 251)',
      text: 'rgb(17, 24, 39)',
    },
    fonts: {
      heading: 'font-sans',
      body: 'font-sans',
    },
    layouts: {
      title: {
        background: {
          type: 'gradient',
          colors: ['rgb(37, 99, 235)', 'rgb(79, 70, 229)'],
        },
        textColor: 'text-white',
      },
      content: {
        background: {
          type: 'solid',
          color: 'rgb(249, 250, 251)',
        },
        textColor: 'text-gray-900',
      },
    },
  },
  elegant: {
    name: 'Elegant',
    colors: {
      primary: 'rgb(55, 65, 81)',
      secondary: 'rgb(107, 114, 128)',
      accent: 'rgb(234, 88, 12)',
      background: 'rgb(255, 255, 255)',
      text: 'rgb(17, 24, 39)',
    },
    fonts: {
      heading: 'font-serif',
      body: 'font-serif',
    },
    layouts: {
      title: {
        background: {
          type: 'pattern',
          color: 'rgb(55, 65, 81)',
        },
        textColor: 'text-white',
      },
      content: {
        background: {
          type: 'solid',
          color: 'rgb(255, 255, 255)',
        },
        textColor: 'text-gray-900',
      },
    },
  },
  vibrant: {
    name: 'Vibrant',
    colors: {
      primary: 'rgb(236, 72, 153)',
      secondary: 'rgb(217, 70, 239)',
      accent: 'rgb(139, 92, 246)',
      background: 'rgb(255, 255, 255)',
      text: 'rgb(17, 24, 39)',
    },
    fonts: {
      heading: 'font-sans',
      body: 'font-sans',
    },
    layouts: {
      title: {
        background: {
          type: 'gradient',
          colors: ['rgb(236, 72, 153)', 'rgb(139, 92, 246)'],
        },
        textColor: 'text-white',
      },
      content: {
        background: {
          type: 'solid',
          color: 'rgb(255, 255, 255)',
        },
        textColor: 'text-gray-900',
      },
    },
  },
};

export const PresentationThemeProvider = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState(themes.modern);

  const value = {
    theme: currentTheme,
    setTheme: (themeName) => {
      const newTheme = themes[themeName];
      if (newTheme) {
        setCurrentTheme(newTheme);
      }
    },
    themes,
  };

  return (
    <PresentationThemeContext.Provider value={value}>
      {children}
    </PresentationThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(PresentationThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a PresentationThemeProvider');
  }
  return context;
};
