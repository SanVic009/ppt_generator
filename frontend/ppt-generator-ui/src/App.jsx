import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [socket, setSocket] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [numSlides, setNumSlides] = useState(5);
  const [selectedTheme, setSelectedTheme] = useState('corporate_blue');
  const [availableThemes, setAvailableThemes] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentProject, setCurrentProject] = useState(null);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    // Fetch available themes
    const fetchThemes = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/themes`);
        if (response.data.success) {
          setAvailableThemes(response.data.themes);
          setSelectedTheme(response.data.default_theme);
          addLog(`Loaded ${response.data.themes.length} available themes`, 'info');
        }
      } catch (error) {
        console.error('Error fetching themes:', error);
        addLog('Failed to load themes, using default', 'warning');
      }
    };

    fetchThemes();

    // Initialize socket connection
    const newSocket = io(API_BASE_URL);
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to server');
      addLog('Connected to PPT Generator', 'success');
    });

    newSocket.on('progress_update', (data) => {
      console.log('Progress update:', data);
      addLog(data.message, 'info');
    });

    newSocket.on('project_completed', (data) => {
      console.log('Project completed:', data);
      setIsGenerating(false);
      setCurrentProject(data);
      addLog('Presentation generated successfully!', 'success');
    });

    newSocket.on('project_failed', (data) => {
      console.log('Project failed:', data);
      setIsGenerating(false);
      addLog(`Presentation generation failed: ${data.error}`, 'error');
    });

    return () => {
      newSocket.close();
    };
  }, []);

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { message, type, timestamp, id: Date.now() }]);
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      addLog('Please enter a presentation description', 'warning');
      return;
    }

    if (numSlides < 1 || numSlides > 20) {
      addLog('Number of slides must be between 1 and 20', 'warning');
      return;
    }

    setIsGenerating(true);
    setCurrentProject(null);
    addLog('Starting presentation generation...', 'info');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/generate`, {
        prompt: prompt.trim(),
        num_slides: numSlides,
        theme: selectedTheme
      });

      if (response.data.project_id) {
        addLog(`Presentation started with ID: ${response.data.project_id}`, 'success');
        socket.emit('join_project', { project_id: response.data.project_id });
      }
    } catch (error) {
      console.error('Error starting generation:', error);
      setIsGenerating(false);
      addLog(`Failed to start generation: ${error.message}`, 'error');
    }
  };

  const handleDownload = async () => {
    if (!currentProject?.project_id) return;

    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/projects/${currentProject.project_id}/download`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `presentation_${currentProject.project_id}.pptx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      addLog('Presentation downloaded successfully!', 'success');
    } catch (error) {
      console.error('Error downloading presentation:', error);
      addLog(`Failed to download presentation: ${error.message}`, 'error');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-green-400 to-purple-500 bg-clip-text text-transparent">
            PPT Generator
          </h1>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            Transform your ideas into beautiful presentations using AI-powered multi-agent system.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Presentation Details</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Presentation Description</label>
                <textarea
                  className="w-full h-32 p-3 bg-gray-700 rounded-lg text-white resize-none"
                  placeholder="Example: Create a presentation about artificial intelligence and its impact on modern business..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  disabled={isGenerating}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Number of Slides</label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  className="w-full p-3 bg-gray-700 rounded-lg text-white"
                  value={numSlides}
                  onChange={(e) => setNumSlides(parseInt(e.target.value) || 5)}
                  disabled={isGenerating}
                />
                <p className="text-xs text-gray-400 mt-1">Between 1 and 20 slides</p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-3">Presentation Theme</label>
                
                {/* Custom Theme Selector */}
                <div className="space-y-3">
                  {/* Current Selection Display */}
                  <div className="relative">
                    <select
                      className="w-full p-4 bg-gray-700 border-2 border-gray-600 rounded-lg text-white 
                                appearance-none cursor-pointer hover:border-gray-500 focus:border-blue-500 
                                focus:outline-none transition-colors text-base"
                      value={selectedTheme}
                      onChange={(e) => setSelectedTheme(e.target.value)}
                      disabled={isGenerating}
                    >
                      {availableThemes.map((theme) => (
                        <option key={theme.id} value={theme.id} className="bg-gray-700 text-white">
                          {theme.name}
                        </option>
                      ))}
                    </select>
                    {/* Custom dropdown arrow */}
                    <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>
                  
                  {/* Theme Preview */}
                  {availableThemes.find(t => t.id === selectedTheme) && (
                    <div className="p-4 bg-gray-600 border border-gray-500 rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-white mb-1">
                            {availableThemes.find(t => t.id === selectedTheme).name}
                          </h4>
                          <p className="text-gray-300 text-sm mb-3">
                            {availableThemes.find(t => t.id === selectedTheme).description}
                          </p>
                        </div>
                      </div>
                      
                      {/* Color Preview */}
                      <div className="flex items-center space-x-3">
                        <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                          Color Palette:
                        </span>
                        <div className="flex space-x-2">
                          <div 
                            className="w-6 h-6 rounded-full border-2 border-white shadow-sm"
                            style={{ 
                              backgroundColor: availableThemes.find(t => t.id === selectedTheme).preview_colors.primary.replace('rgb(', 'rgba(').replace(')', ', 1)')
                            }}
                            title="Primary Color"
                          ></div>
                          <div 
                            className="w-6 h-6 rounded-full border-2 border-white shadow-sm"
                            style={{ 
                              backgroundColor: availableThemes.find(t => t.id === selectedTheme).preview_colors.secondary.replace('rgb(', 'rgba(').replace(')', ', 1)')
                            }}
                            title="Secondary Color"
                          ></div>
                          <div 
                            className="w-6 h-6 rounded-full border-2 border-white shadow-sm"
                            style={{ 
                              backgroundColor: availableThemes.find(t => t.id === selectedTheme).preview_colors.accent.replace('rgb(', 'rgba(').replace(')', ', 1)')
                            }}
                            title="Accent Color"
                          ></div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Quick Theme Grid (Optional - for quick selection) */}
                  <div className="grid grid-cols-3 gap-2 mt-3">
                    {availableThemes.slice(0, 6).map((theme) => (
                      <button
                        key={theme.id}
                        onClick={() => setSelectedTheme(theme.id)}
                        disabled={isGenerating}
                        className={`p-2 rounded-lg border-2 transition-all text-xs
                          ${selectedTheme === theme.id 
                            ? 'border-blue-500 bg-blue-500/20' 
                            : 'border-gray-600 bg-gray-700 hover:border-gray-500'
                          } ${isGenerating ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                      >
                        <div className="flex space-x-1 justify-center mb-1">
                          <div 
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: theme.preview_colors.primary.replace('rgb(', 'rgba(').replace(')', ', 1)') }}
                          ></div>
                          <div 
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: theme.preview_colors.secondary.replace('rgb(', 'rgba(').replace(')', ', 1)') }}
                          ></div>
                          <div 
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: theme.preview_colors.accent.replace('rgb(', 'rgba(').replace(')', ', 1)') }}
                          ></div>
                        </div>
                        <div className="text-white font-medium text-xs truncate">
                          {theme.name}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 space-y-2">
              <button 
                onClick={handleGenerate}
                disabled={isGenerating || !prompt.trim()}
                className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white py-3 px-4 rounded-lg transition-colors"
              >
                {isGenerating ? 'Generating...' : 'Generate Presentation'}
              </button>

              {currentProject?.result?.success && (
                <button 
                  onClick={handleDownload}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg transition-colors"
                >
                  Download Presentation
                </button>
              )}
            </div>
          </div>

          {/* Logs Section */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Live Logs</h2>
            <div className="h-80 overflow-y-auto bg-gray-900 rounded-lg p-3">
              {logs.length === 0 ? (
                <p className="text-gray-400">No logs yet. Start generating a presentation to see live updates.</p>
              ) : (
                logs.map((log) => (
                  <div key={log.id} className={`mb-2 p-2 rounded text-sm ${
                    log.type === 'success' ? 'bg-green-900 text-green-200' :
                    log.type === 'warning' ? 'bg-yellow-900 text-yellow-200' :
                    log.type === 'error' ? 'bg-red-900 text-red-200' :
                    'bg-blue-900 text-blue-200'
                  }`}>
                    <div className="flex justify-between">
                      <span>{log.message}</span>
                      <span className="text-xs opacity-70">{log.timestamp}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Presentation Results */}
        {currentProject?.result?.success && (
          <div className="mt-8 bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-green-400">Presentation Generated Successfully</h2>
            {currentProject.result.presentation_plan && (
              <div className="bg-gray-700 p-4 rounded-lg">
                <p><strong>Title:</strong> {currentProject.result.presentation_plan.presentation_title}</p>
                <p><strong>Description:</strong> {currentProject.result.presentation_plan.presentation_description}</p>
                <p><strong>Total Slides:</strong> {currentProject.result.presentation_plan.total_slides}</p>
                <p><strong>Theme:</strong> {availableThemes.find(t => t.id === selectedTheme)?.name || selectedTheme}</p>
              </div>
            )}
          </div>
        )}

        {/* Available Themes Preview */}
        {availableThemes.length > 0 && (
          <div className="mt-8 bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Available Themes</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableThemes.map((theme) => (
                <div 
                  key={theme.id}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedTheme === theme.id 
                      ? 'border-green-500 bg-gray-700' 
                      : 'border-gray-600 bg-gray-750 hover:border-gray-500'
                  }`}
                  onClick={() => setSelectedTheme(theme.id)}
                >
                  <h3 className="font-semibold text-sm mb-2">{theme.name}</h3>
                  <p className="text-xs text-gray-400 mb-3">{theme.description}</p>
                  <div className="flex space-x-2">
                    <div 
                      className="w-6 h-6 rounded"
                      style={{ backgroundColor: theme.preview_colors.primary.replace('rgb(', 'rgba(').replace(')', ', 1)') }}
                      title="Primary"
                    ></div>
                    <div 
                      className="w-6 h-6 rounded"
                      style={{ backgroundColor: theme.preview_colors.secondary.replace('rgb(', 'rgba(').replace(')', ', 1)') }}
                      title="Secondary"
                    ></div>
                    <div 
                      className="w-6 h-6 rounded"
                      style={{ backgroundColor: theme.preview_colors.accent.replace('rgb(', 'rgba(').replace(')', ', 1)') }}
                      title="Accent"
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Agent Information */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-3 text-blue-400">Planner Agent</h3>
            <p className="text-sm text-gray-300">
              Analyzes your requirements and creates a comprehensive presentation blueprint.
            </p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-3 text-purple-400">Content Creator</h3>
            <p className="text-sm text-gray-300">
              Generates engaging and relevant content for each slide.
            </p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-3 text-green-400">Designer Agent</h3>
            <p className="text-sm text-gray-300">
              Creates visually appealing slide designs with professional layouts.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

