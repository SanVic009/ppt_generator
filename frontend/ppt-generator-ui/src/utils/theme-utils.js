export const generateSlideStyles = (theme, type = 'default') => {
  const baseStyles = {
    background: theme.colors.background,
    color: theme.colors.text,
    fontFamily: theme.fonts.body
  };

  const slideTypes = {
    title: {
      ...baseStyles,
      background: theme.gradients.primary,
      color: '#ffffff',
      '& h1, & h2, & h3': {
        fontFamily: theme.fonts.heading,
        marginBottom: '1.5rem'
      }
    },
    section: {
      ...baseStyles,
      background: theme.gradients.secondary,
      color: '#ffffff',
      '& h1, & h2, & h3': {
        fontFamily: theme.fonts.heading,
        marginBottom: '1rem'
      }
    },
    content: {
      ...baseStyles,
      '& h1, & h2, & h3': {
        color: theme.colors.primary,
        fontFamily: theme.fonts.heading,
        marginBottom: '1rem'
      },
      '& strong': {
        color: theme.colors.secondary
      },
      '& ul, & ol': {
        marginLeft: '1.5rem',
        marginBottom: '1rem'
      },
      '& li': {
        marginBottom: '0.5rem'
      }
    },
    image: {
      ...baseStyles,
      '& figure': {
        margin: '1rem 0',
        '& img': {
          maxWidth: '100%',
          height: 'auto',
          borderRadius: '0.5rem'
        },
        '& figcaption': {
          marginTop: '0.5rem',
          fontSize: '0.875rem',
          color: theme.colors.secondary
        }
      }
    },
    quote: {
      ...baseStyles,
      background: theme.patterns.dots,
      '& blockquote': {
        borderLeft: `4px solid ${theme.colors.primary}`,
        padding: '1rem 0 1rem 1.5rem',
        margin: '1rem 0',
        fontStyle: 'italic',
        '& cite': {
          display: 'block',
          marginTop: '0.5rem',
          color: theme.colors.secondary,
          fontSize: '0.875rem'
        }
      }
    }
  };

  return slideTypes[type] || slideTypes.content;
};

export const generateTransitionStyles = (theme) => {
  return {
    fade: {
      enter: {
        opacity: 0
      },
      enterActive: {
        opacity: 1,
        transition: 'opacity 300ms ease-in-out'
      },
      exit: {
        opacity: 0,
        transition: 'opacity 300ms ease-in-out'
      }
    },
    slide: {
      enter: {
        transform: 'translateX(100%)'
      },
      enterActive: {
        transform: 'translateX(0)',
        transition: 'transform 300ms ease-in-out'
      },
      exit: {
        transform: 'translateX(-100%)',
        transition: 'transform 300ms ease-in-out'
      }
    },
    scale: {
      enter: {
        transform: 'scale(0.9)',
        opacity: 0
      },
      enterActive: {
        transform: 'scale(1)',
        opacity: 1,
        transition: 'all 300ms ease-in-out'
      },
      exit: {
        transform: 'scale(0.9)',
        opacity: 0,
        transition: 'all 300ms ease-in-out'
      }
    }
  };
};

export const applyThemeToSlide = (slide, theme) => {
  const styles = generateSlideStyles(theme, slide.type);
  return {
    ...slide,
    styles,
    transition: generateTransitionStyles(theme).fade
  };
};

export const applyThemeToPresentation = (presentation, theme) => {
  return {
    ...presentation,
    slides: presentation.slides.map(slide => applyThemeToSlide(slide, theme)),
    theme: theme.name,
    styles: {
      background: theme.colors.background,
      color: theme.colors.text,
      fontFamily: theme.fonts.body
    }
  };
};
