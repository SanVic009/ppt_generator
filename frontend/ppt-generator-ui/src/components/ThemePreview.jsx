import React from 'react';
import { Card } from './ui/card';

const ThemePreview = ({ theme, onSelect, isSelected }) => {
  const {
    colors,
    fonts,
  } = theme;

  return (
    <Card
      className={`
        relative overflow-hidden cursor-pointer transition-all duration-300
        ${isSelected ? 'ring-2 ring-primary' : 'hover:shadow-lg'}
      `}
      onClick={() => onSelect()}
    >
      <div className="aspect-video p-4" style={{ background: colors.background }}>
        {/* Title slide preview */}
        <div
          className="w-full h-1/2 mb-2 rounded-lg p-4"
          style={{
            background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
          }}
        >
          <h3
            className="text-white text-lg font-bold truncate"
            style={{ fontFamily: fonts.heading }}
          >
            Sample Title
          </h3>
          <p
            className="text-white/80 text-sm"
            style={{ fontFamily: fonts.body }}
          >
            Subtitle text
          </p>
        </div>

        {/* Content slide preview */}
        <div className="w-full h-1/2 bg-white rounded-lg p-4">
          <h4
            className="text-sm font-semibold mb-1"
            style={{
              fontFamily: fonts.heading,
              color: colors.primary,
            }}
          >
            Content Slide
          </h4>
          <div
            className="flex gap-2"
            style={{
              fontFamily: fonts.body,
              color: colors.text,
            }}
          >
            <div className="w-1/2 h-8 bg-gray-100 rounded"></div>
            <div className="w-1/2 space-y-1">
              <div className="h-2 w-full bg-gray-100 rounded"></div>
              <div className="h-2 w-3/4 bg-gray-100 rounded"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Theme name */}
      <div className="p-3 border-t">
        <p className="text-sm font-medium">{theme.name}</p>
        <div className="flex gap-1 mt-1">
          {[colors.primary, colors.secondary, colors.accent].map((color, i) => (
            <div
              key={i}
              className="w-4 h-4 rounded-full"
              style={{ backgroundColor: color }}
            />
          ))}
        </div>
      </div>
    </Card>
  );
};

export default ThemePreview;
