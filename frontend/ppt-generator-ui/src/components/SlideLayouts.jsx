import React from 'react';
import { useTheme } from '../contexts/PresentationThemeContext';

export const TitleSlide = ({ title, subtitle, background }) => {
  const { theme } = useTheme();
  
  return (
    <div 
      className="min-h-screen flex flex-col justify-center items-center p-12"
      style={{
        background: background || `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.secondary})`,
      }}
    >
      <h1 className={`
        ${theme.fonts.heading}
        text-6xl md:text-8xl font-bold mb-8
        text-white drop-shadow-lg
        animate-fade-in
      `}>
        {title}
      </h1>
      {subtitle && (
        <p className={`
          ${theme.fonts.body}
          text-2xl md:text-3xl
          text-white/90
          animate-fade-in-delayed
        `}>
          {subtitle}
        </p>
      )}
    </div>
  );
};

export const ContentSlide = ({ title, content, layout = 'standard', background }) => {
  const { theme } = useTheme();
  
  const layouts = {
    standard: 'flex flex-col space-y-6',
    'two-column': 'grid grid-cols-2 gap-8',
    'image-left': 'grid grid-cols-2 gap-8',
    'image-right': 'grid grid-cols-2 gap-8',
  };

  return (
    <div 
      className="min-h-screen p-12"
      style={{
        background: background || theme.colors.background,
      }}
    >
      <div className={layouts[layout]}>
        <h2 className={`
          ${theme.fonts.heading}
          text-4xl font-bold mb-8
          ${background ? 'text-white drop-shadow-lg' : 'text-gray-900'}
        `}>
          {title}
        </h2>
        <div className={`
          ${theme.fonts.body}
          prose prose-lg max-w-none
          ${background ? 'text-white prose-invert' : 'text-gray-700'}
        `}>
          {content}
        </div>
      </div>
    </div>
  );
};

export const ImageContentSlide = ({ title, content, image, layout = 'image-right' }) => {
  const { theme } = useTheme();
  
  return (
    <div className="min-h-screen p-12" style={{ background: theme.colors.background }}>
      <div className={`grid grid-cols-2 gap-8 ${layout === 'image-left' ? 'flex-row-reverse' : ''}`}>
        <div className="flex flex-col justify-center">
          <h2 className={`${theme.fonts.heading} text-4xl font-bold mb-8 text-gray-900`}>
            {title}
          </h2>
          <div className={`${theme.fonts.body} prose prose-lg max-w-none text-gray-700`}>
            {content}
          </div>
        </div>
        <div className="flex items-center justify-center">
          <img
            src={image}
            alt={title}
            className="max-w-full h-auto rounded-lg shadow-lg"
          />
        </div>
      </div>
    </div>
  );
};

export const QuoteSlide = ({ quote, author, background }) => {
  const { theme } = useTheme();
  
  return (
    <div 
      className="min-h-screen flex flex-col justify-center items-center p-12"
      style={{
        background: background || `linear-gradient(135deg, ${theme.colors.secondary}, ${theme.colors.accent})`,
      }}
    >
      <blockquote className="max-w-4xl text-center">
        <p className={`
          ${theme.fonts.heading}
          text-4xl md:text-5xl font-bold mb-8
          text-white drop-shadow-lg
          leading-relaxed
        `}>
          "{quote}"
        </p>
        {author && (
          <footer className={`
            ${theme.fonts.body}
            text-xl md:text-2xl
            text-white/90
            mt-8
          `}>
            — {author}
          </footer>
        )}
      </blockquote>
    </div>
  );
};

export const GridSlide = ({ title, items }) => {
  const { theme } = useTheme();
  
  return (
    <div className="min-h-screen p-12" style={{ background: theme.colors.background }}>
      <h2 className={`${theme.fonts.heading} text-4xl font-bold mb-12 text-gray-900`}>
        {title}
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
        {items.map((item, index) => (
          <div 
            key={index}
            className="bg-white p-6 rounded-lg shadow-lg"
          >
            {item.icon && (
              <div className="text-4xl mb-4 text-primary">
                {item.icon}
              </div>
            )}
            <h3 className={`${theme.fonts.heading} text-xl font-bold mb-4`}>
              {item.title}
            </h3>
            <p className={`${theme.fonts.body} text-gray-600`}>
              {item.content}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
