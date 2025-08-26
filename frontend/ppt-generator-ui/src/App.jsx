import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from './context/theme-context.jsx';
import PresentationForm from './components/PresentationForm';
import PresentationPreview from './components/PresentationPreview';
import { ThemePreview } from './components/theme-preview';
import { Alert, AlertTitle, AlertDescription } from './components/ui/alert';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [socket, setSocket] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentProject, setCurrentProject] = useState(null);
  const [logs, setLogs] = useState([]);
  
  const {
    theme,
    currentTheme,
    switchTheme,
    availableThemes
  } = useTheme();

  // Remove the useEffect for fetching themes since we're using our theme system now

  const connectToSocket = (projectId) => {
    const newSocket = io(API_BASE_URL);
    
    newSocket.on('connect', () => {
      addLog('Connected to server', 'info');
      newSocket.emit('join', { room: projectId });
    });

    newSocket.on('status_update', (data) => {
      addLog(data.message, data.type || 'info');
    });

    newSocket.on('disconnect', () => {
      addLog('Disconnected from server', 'warning');
    });

    setSocket(newSocket);

    return () => newSocket.close();
  };

  const addLog = (message, type = 'info') => {
    setLogs((prev) => [...prev, { message, type, timestamp: new Date() }]);
  };

  const handleSubmit = async (formData) => {
    console.log('handleSubmit called', formData);
    setIsGenerating(true);
    
    try {
      // Create new presentation project
      const createResponse = await axios.post(`${API_BASE_URL}/api/presentations`, {
        title: formData.title,
        description: formData.description,
        style_preferences: {
          theme: formData.theme,
          num_slides: formData.numSlides
        }
      });
      
      if (createResponse.data.status === 'success') {
        const projectId = createResponse.data.project_id;
        setCurrentProject(projectId);
        addLog(`Created new presentation project`, 'info');
        
        // Connect to websocket for real-time updates
        connectToSocket(projectId);
        
        // Start generation
        const generateResponse = await axios.post(
          `${API_BASE_URL}/api/presentations/${projectId}/generate`,
          {
            topic: formData.title,
            additional_info: formData.description
          }
        );
        
        if (generateResponse.data.status === 'success') {
          addLog('Generation completed successfully', 'success');
        }
      }
    } catch (error) {
      console.error('Error generating presentation:', error);
      addLog('Failed to generate presentation', 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
      <motion.div 
        className="min-h-screen"
        style={{ 
          backgroundColor: theme?.colors?.background || '#ffffff',
          color: theme?.colors?.text || '#000000'
        }}
      >
        <header 
          className="border-b"
          style={{
            background: theme?.gradients?.primary || `linear-gradient(135deg, ${theme?.colors?.primary || '#1a73e8'}, ${theme?.colors?.secondary || '#4285f4'})`,
            color: '#ffffff'
          }}
        >
          <motion.div 
            className="max-w-7xl mx-auto px-4 py-6"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-3xl font-bold" style={{ fontFamily: theme.fonts.heading }}>
              AI Presentation Generator
            </h1>
          </motion.div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
            {/* Left side - Form */}
            <div className="xl:col-span-5 space-y-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
              >
                <PresentationForm
                  onSubmit={handleSubmit}
                  isGenerating={isGenerating}
                />
              </motion.div>
              
              {/* Theme Previews */}
              <motion.div
                className="bg-white/50 backdrop-blur-sm p-6 rounded-lg shadow-lg"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <h2 className="text-xl font-semibold mb-4" style={{ fontFamily: theme.fonts.heading }}>
                  Available Themes
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  <AnimatePresence mode="popLayout">
                    {availableThemes.map((themeItem) => (
                      <ThemePreview
                        key={themeItem.id}
                        theme={themeItem}
                        name={themeItem.name}
                        isActive={currentTheme === themeItem.id}
                        onSelect={() => switchTheme(themeItem.id)}
                      />
                    ))}
                  </AnimatePresence>
                </div>
              </motion.div>
            </div>

            {/* Right side - Preview and Logs */}
            <div className="xl:col-span-7 space-y-6">
              {/* Preview section */}
              <motion.div 
                className="sticky top-8 bg-white/50 backdrop-blur-sm rounded-lg shadow-lg"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
              >
                {currentProject ? (
                  <PresentationPreview 
                    presentationId={currentProject}
                    theme={theme}
                  />
                ) : (
                  <div 
                    className="aspect-video flex items-center justify-center"
                    style={{ color: theme.colors.secondary }}
                  >
                    Your presentation preview will appear here
                  </div>
                )}
              </motion.div>

              {/* Logs section */}
              <motion.div 
                className="bg-white/50 backdrop-blur-sm rounded-lg shadow-lg p-4 space-y-2 max-h-96 overflow-auto"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                <h3 className="font-semibold mb-2" style={{ fontFamily: theme.fonts.heading }}>
                  Generation Progress
                </h3>
                <AnimatePresence mode="popLayout">
                  {logs.map((log, index) => (
                    <motion.div
                      key={`${log.timestamp}-${index}`}
                      layout
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Alert variant={log.type}>
                        <AlertTitle>
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </AlertTitle>
                        <AlertDescription>{log.message}</AlertDescription>
                      </Alert>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </motion.div>
            </div>
          </div>
        </main>
      </motion.div>
  );
}

export default App;