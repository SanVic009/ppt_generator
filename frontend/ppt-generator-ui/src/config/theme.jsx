export const defaultThemes = {
  corporate_blue: {
    id: 'corporate_blue',
    name: 'Corporate Blue',
    colors: {
      primary: '#1a73e8',
      secondary: '#4285f4',
      accent: '#34a853',
      background: '#ffffff',
      background_end: '#f8f9fa',
      text: '#202124',
      text_secondary: '#5f6368',
      text_light: '#ffffff'
    },
    fonts: {
      title: 'Arial',
      content: 'Roboto',
      heading: 'Arial',
      body: 'Roboto',
      sizes: {
        title: 44,
        subtitle: 32,
        content: 18,
        bullet: 16
      }
    },
    gradient: {
      angle: 135
    },
    iconStyle: 'modern',
    layoutPreference: 'balanced'
  },
  elegant_dark: {
    id: 'elegant_dark',
    name: 'Elegant Dark',
    colors: {
      primary: '#9333ea',
      secondary: '#6366f1',
      accent: '#ec4899',
      background: '#18181b',
      background_end: '#27272a',
      text: '#ffffff',
      text_secondary: '#a1a1aa',
      text_light: '#ffffff'
    },
    fonts: {
      title: 'Playfair Display',
      content: 'Inter',
      heading: 'Playfair Display',
      body: 'Inter',
      sizes: {
        title: 44,
        subtitle: 32,
        content: 18,
        bullet: 16
      }
    },
    gradient: {
      angle: 135
    },
    iconStyle: 'minimal',
    layoutPreference: 'balanced'
  },
  nature_green: {
    id: 'nature_green',
    name: 'Nature Green',
    colors: {
      primary: '#059669',
      secondary: '#10b981',
      accent: '#34d399',
      background: '#f0fdf4',
      background_end: '#dcfce7',
      text: '#064e3b',
      text_secondary: '#059669',
      text_light: '#ffffff'
    },
    fonts: {
      title: 'Montserrat',
      content: 'Source Sans Pro',
      heading: 'Montserrat',
      body: 'Source Sans Pro',
      sizes: {
        title: 44,
        subtitle: 32,
        content: 18,
        bullet: 16
      }
    },
    gradient: {
      angle: 120
    },
    iconStyle: 'creative',
    layoutPreference: 'visual_focused'
  },
  modern_gradient: {
    id: 'modern_gradient',
    name: 'Modern Gradient',
    colors: {
      primary: '#6366f1',
      secondary: '#8b5cf6',
      accent: '#ec4899',
      background: '#ffffff',
      background_end: '#f3f4f6',
      text: '#111827',
      text_secondary: '#4b5563',
      text_light: '#ffffff'
    },
    fonts: {
      title: 'Inter',
      content: 'Inter',
      heading: 'Inter',
      body: 'Inter',
      sizes: {
        title: 44,
        subtitle: 32,
        content: 18,
        bullet: 16
      }
    },
    gradient: {
      angle: 145
    },
    iconStyle: 'modern',
    layoutPreference: 'visual_focused',
    gradients: {
      primary: `linear-gradient(${145}deg, #6366f1, #8b5cf6)`,
      secondary: `linear-gradient(${145}deg, #8b5cf6, #ec4899)`,
      accent: `linear-gradient(${145}deg, #ec4899, #6366f1)`
    }
  }
};

// Helper function to get CSS variables from a theme
export function getThemeVariables(theme) {
  return {
    '--theme-primary': theme.colors.primary,
    '--theme-secondary': theme.colors.secondary,
    '--theme-accent': theme.colors.accent,
    '--theme-background': theme.colors.background,
    '--theme-background-end': theme.colors.background_end,
    '--theme-text': theme.colors.text,
    '--theme-text-secondary': theme.colors.text_secondary,
    '--theme-text-light': theme.colors.text_light,
    '--theme-gradient-angle': `${theme.gradient.angle}deg`,
    '--theme-font-title': theme.fonts.title,
    '--theme-font-content': theme.fonts.content,
    '--theme-gradient-primary': theme.gradients?.primary || `linear-gradient(${theme.gradient.angle}deg, ${theme.colors.primary}, ${theme.colors.secondary})`,
    '--theme-gradient-secondary': theme.gradients?.secondary || `linear-gradient(${theme.gradient.angle}deg, ${theme.colors.secondary}, ${theme.colors.accent})`,
    '--theme-gradient-accent': theme.gradients?.accent || `linear-gradient(${theme.gradient.angle}deg, ${theme.colors.accent}, ${theme.colors.primary})`
  };
}

export const defaultAnimations = {
  slideIn: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.3 }
  },
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.3 }
  },
  scaleIn: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
    transition: { duration: 0.3 }
  }
};

export const defaultLayouts = {
  title: {
    container: 'min-h-screen flex flex-col justify-center items-center relative overflow-hidden',
    content: 'text-center z-10 px-8 py-16 max-w-5xl mx-auto',
    heading: 'text-5xl md:text-7xl font-bold mb-6',
    subtitle: 'text-xl md:text-2xl opacity-90'
  },
  content: {
    container: 'min-h-screen flex flex-col justify-center relative',
    content: 'max-w-6xl mx-auto px-8 py-16',
    heading: 'text-4xl font-bold mb-8',
    body: 'prose prose-lg max-w-none'
  },
  split: {
    container: 'min-h-screen grid grid-cols-1 md:grid-cols-2 gap-12',
    content: 'flex flex-col justify-center px-8 py-16',
    heading: 'text-4xl font-bold mb-6',
    body: 'prose prose-lg'
  }
};
