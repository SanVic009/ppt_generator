import React from 'react';

const NavigationButtons = ({ onPrevious, onNext }) => (
  <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 flex gap-4 z-50">
    <button
      onClick={onPrevious}
      className="w-12 h-12 rounded-full bg-black/30 hover:bg-black/50 text-white flex items-center justify-center backdrop-blur-sm transition-all"
      aria-label="Previous slide"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="w-6 h-6"
      >
        <path d="M15 18l-6-6 6-6" />
      </svg>
    </button>
    <button
      onClick={onNext}
      className="w-12 h-12 rounded-full bg-black/30 hover:bg-black/50 text-white flex items-center justify-center backdrop-blur-sm transition-all"
      aria-label="Next slide"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="w-6 h-6"
      >
        <path d="M9 18l6-6-6-6" />
      </svg>
    </button>
  </div>
);

export default NavigationButtons;
