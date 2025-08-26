import React from "react";
import { motion } from "framer-motion";
import { Card } from "./ui/card";
import { Button } from "./ui/button";

const ThemePreview = React.forwardRef(({
  theme,
  name,
  isActive,
  onSelect,
  className = ""
}, ref) => {
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className={className}
    >
      <Card
        className={"p-4 cursor-pointer transition-all hover:scale-105 " + (isActive ? 'ring-2 ring-primary' : '')}
        onClick={() => onSelect(theme.id)}
      >
        <div className="space-y-4">
          {/* Theme Name */}
          <h3 className="font-semibold text-lg">{theme?.name || name}</h3>

          {/* Color Swatches */}
          <div className="grid grid-cols-5 gap-2">
            {theme?.colors && Object.entries(theme.colors)
              .filter(([key]) => !key.includes('_end') && !key.includes('background'))
              .map(([key, color]) => (
                <div
                  key={theme.id + "-color-" + key}
                  className="w-6 h-6 rounded-full"
                  style={{ backgroundColor: color }}
                  title={key}
                />
              ))}
          </div>

          {/* Background Preview */}
          <div
            className="h-12 rounded-md"
            style={{
              background: theme?.gradients?.primary ||
                "linear-gradient(135deg, " + (theme?.colors?.background || '#ffffff') + ", " + (theme?.colors?.background_end || '#f8f9fa') + ")"
            }}
          />

          {/* Font Preview */}
          <div className="space-y-2">
            <p
              className="text-sm truncate"
              style={{ fontFamily: theme?.fonts?.title }}
            >
              {theme?.fonts?.title || 'Default Title Font'}
            </p>
            <p
              className="text-xs truncate opacity-80"
              style={{ fontFamily: theme?.fonts?.content }}
            >
              {theme?.fonts?.content || 'Default Content Font'}
            </p>
          </div>

          {/* Theme Status */}
          {isActive && (
            <div className="flex items-center justify-center">
              <Button variant="ghost" size="sm" className="text-xs">
                Currently Active
              </Button>
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  );
});

export { ThemePreview };