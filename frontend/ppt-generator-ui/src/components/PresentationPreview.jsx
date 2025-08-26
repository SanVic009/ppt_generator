import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';

const PresentationPreview = ({ presentationId, theme }) => {
  const [presentation, setPresentation] = useState(null);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchPresentation = async () => {
      try {
        const response = await fetch(`/api/presentations/${presentationId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch presentation');
        }
        
        const data = await response.json();
        setPresentation(data.presentation);
        setIsLoading(false);
      } catch (err) {
        setError(err.message);
        setIsLoading(false);
      }
    };
    
    if (presentationId) {
      fetchPresentation();
    }
  }, [presentationId]);
  
  const handlePrevious = () => {
    setCurrentSlideIndex((prev) => 
      prev > 0 ? prev - 1 : presentation.slides.length - 1
    );
  };

  const handleNext = () => {
    setCurrentSlideIndex((prev) => 
      prev < presentation.slides.length - 1 ? prev + 1 : 0
    );
  };

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === 'ArrowLeft') handlePrevious();
      if (e.key === 'ArrowRight') handleNext();
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [presentation]);
  
  if (isLoading) {
    return (
      <Card className="aspect-video flex items-center justify-center">
        <motion.div
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [1, 0.8, 1]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="text-primary"
        >
          Loading presentation...
        </motion.div>
      </Card>
    );
  }
  
  if (error) {
    return (
      <Card className="aspect-video flex items-center justify-center">
        <div className="text-destructive">Error: {error}</div>
      </Card>
    );
  }
  
  if (!presentation) {
    return (
      <Card className="aspect-video flex items-center justify-center">
        <div className="text-muted-foreground">No presentation loaded</div>
      </Card>
    );
  }
  
  const openFullscreen = () => {
    window.open(`/api/presentations/${presentationId}?format=html`, '_blank');
  };

  const downloadPDF = () => {
    window.open(`/api/presentations/${presentationId}/download/pdf`, '_blank');
  };

  const downloadResponse = () => {
    window.open(`/api/presentations/${presentationId}/download/response`, '_blank');
  };
  
  const currentSlide = presentation.slides[currentSlideIndex];
  
  return (
    <div className="relative group">
      {/* Main slide container */}
      <Card className="aspect-video overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentSlideIndex}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
            className="h-full w-full p-8 relative"
            style={{
              background: theme?.gradients?.primary || 'linear-gradient(135deg, hsl(var(--primary)), hsl(var(--secondary)))',
              color: 'white',
              fontFamily: theme?.fonts?.body
            }}
          >
            <>
                <div className="absolute top-4 left-4 right-4 flex justify-between items-center">
                  <h1 className="text-xl font-bold">{presentation.title}</h1>
                  <Button
                    variant="ghost"
                    onClick={openFullscreen}
                    className="bg-background/20 backdrop-blur-sm hover:bg-background/40"
                  >
                    Present
                  </Button>
                </div>
                <div className="h-full flex items-center justify-center">
                  {currentSlide?.content}
                </div>
              </>
          </motion.div>
        </AnimatePresence>
      </Card>

      {/* Navigation controls */}
      <div className="absolute inset-y-0 left-0 flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
        <Button
          variant="ghost"
          size="icon"
          onClick={handlePrevious}
          disabled={currentSlideIndex === 0}
          className="ml-2 bg-background/20 backdrop-blur-sm hover:bg-background/40"
        >
          <ChevronLeft className="h-6 w-6" />
        </Button>
      </div>

      <div className="absolute inset-y-0 right-0 flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleNext}
          disabled={currentSlideIndex === (presentation?.slides.length ?? 0) - 1}
          className="mr-2 bg-background/20 backdrop-blur-sm hover:bg-background/40"
        >
          <ChevronRight className="h-6 w-6" />
        </Button>
      </div>

      {/* Progress indicator */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
        {presentation?.slides.map((_, index) => (
          <motion.button
            key={index}
            className={`w-2 h-2 rounded-full transition-all ${
              index === currentSlideIndex 
                ? 'bg-white' 
                : 'bg-white/40 hover:bg-white/60'
            }`}
            onClick={() => setCurrentSlideIndex(index)}
            whileHover={{ scale: 1.2 }}
            whileTap={{ scale: 0.9 }}
          />
        ))}
      </div>

      {/* Slide counter */}
      <div className="absolute bottom-4 right-4 px-3 py-1 rounded-full bg-background/20 backdrop-blur-sm text-sm text-white">
        {currentSlideIndex + 1} / {presentation?.slides.length ?? 0}
      </div>
    </div>
  );
};

export default PresentationPreview;
