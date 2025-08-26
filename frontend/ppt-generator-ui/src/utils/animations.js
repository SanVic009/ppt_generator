import { useEffect } from 'react';

export const useSlideAnimation = (selector, options = {}) => {
  useEffect(() => {
    const animateSlides = () => {
      const slides = document.querySelectorAll(selector);
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('animate-in');
            } else if (options.reset) {
              entry.target.classList.remove('animate-in');
            }
          });
        },
        {
          threshold: options.threshold || 0.1,
          root: options.root || null,
          rootMargin: options.rootMargin || '0px',
        }
      );

      slides.forEach((slide) => {
        observer.observe(slide);
      });

      return () => observer.disconnect();
    };

    return animateSlides();
  }, [selector, options]);
};

export const animations = {
  fadeIn: {
    initial: 'opacity-0',
    animate: 'animate-fade-in',
    transition: 'transition-opacity duration-500 ease-in-out',
  },
  slideUp: {
    initial: 'opacity-0 translate-y-4',
    animate: 'animate-slide-up',
    transition: 'transition-all duration-500 ease-out',
  },
  slideIn: {
    initial: 'opacity-0 -translate-x-4',
    animate: 'animate-slide-in',
    transition: 'transition-all duration-500 ease-out',
  },
  scale: {
    initial: 'opacity-0 scale-95',
    animate: 'animate-scale',
    transition: 'transition-all duration-500 ease-out',
  },
};

export const createKeyframeAnimation = (name, keyframes) => {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes ${name} {
      ${Object.entries(keyframes)
        .map(([key, value]) => `${key} { ${value} }`)
        .join('\n')}
    }
  `;
  document.head.appendChild(style);
};

// Create default animations
createKeyframeAnimation('fade-in', {
  '0%': 'opacity: 0;',
  '100%': 'opacity: 1;',
});

createKeyframeAnimation('slide-up', {
  '0%': 'opacity: 0; transform: translateY(1rem);',
  '100%': 'opacity: 1; transform: translateY(0);',
});

createKeyframeAnimation('slide-in', {
  '0%': 'opacity: 0; transform: translateX(-1rem);',
  '100%': 'opacity: 1; transform: translateX(0);',
});

createKeyframeAnimation('scale', {
  '0%': 'opacity: 0; transform: scale(0.95);',
  '100%': 'opacity: 1; transform: scale(1);',
});
