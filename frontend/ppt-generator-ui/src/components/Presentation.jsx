import React from 'react';

// Custom theme with Tailwind CSS
const CustomTheme = {
  colors: {
    primary: 'rgb(37, 99, 235)', // blue-600
    secondary: 'rgb(79, 70, 229)', // indigo-600
    accent: 'rgb(236, 72, 153)', // pink-500
    background: 'rgb(249, 250, 251)', // gray-50
    text: 'rgb(17, 24, 39)', // gray-900
  },
  fonts: {
    heading: 'font-sans',
    body: 'font-sans',
  },
};

const Presentation = ({ slides = [] }) => {
  const renderSlide = (slide, index) => {
    const {
      type = 'standard',
      title,
      content,
      background,
      layout = 'default',
    } = slide;

    const slideStyle = {
      backgroundImage: background?.image ? `url(${background.image})` : undefined,
      backgroundColor: background?.color || CustomTheme.colors.background,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      height: '100%', // Make each slide take full container height
      width: '100%',
      scrollSnapAlign: 'start', // For smooth scrolling between slides
    };

    const getLayoutClasses = () => {
      switch (layout) {
        case 'title':
          return 'flex flex-col justify-center items-center h-full';
        case 'split':
          return 'grid grid-cols-2 gap-8 h-full';
        case 'image-left':
          return 'grid grid-cols-2 gap-8 h-full';
        default:
          return 'flex flex-col h-full';
      }
    };

    return (
      <section
        key={index}
        data-slide-type={type}
        className="slide relative"
        style={slideStyle}
      >
        <div className={`slide-content p-12 ${getLayoutClasses()}`}>
          {title && (
            <h2 className={`
              ${CustomTheme.fonts.heading}
              text-4xl md:text-6xl font-bold mb-8
              ${type === 'title' ? 'text-center' : ''}
              ${background?.image ? 'text-white drop-shadow-lg' : 'text-gray-900'}
            `}>
              {title}
            </h2>
          )}
          <div className={`
            slide-body
            ${CustomTheme.fonts.body}
            prose prose-lg max-w-none
            ${background?.image ? 'text-white prose-invert' : 'text-gray-700'}
          `}>
            {content}
          </div>
        </div>
      </section>
    );
  };

  return (
    <div className="h-full w-full overflow-y-auto scroll-snap-y-mandatory">
      {slides.map((slide, index) => renderSlide(slide, index))}
    </div>
  );
};

export default Presentation;