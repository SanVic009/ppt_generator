import { useState, useEffect } from 'react'
import { PresentationForm } from './components/PresentationForm'
import { ThemeSelector } from './components/ThemeSelector'
import { GenerationStatus } from './components/GenerationStatus'
import { PresentationList } from './components/PresentationList'
import { Header } from './components/Header'
import { Footer } from './components/Footer'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/Tabs'
import { api } from './services/api'

function App() {
  const [themes, setThemes] = useState([])
  const [selectedTheme, setSelectedTheme] = useState('corporate_blue')
  const [activeProject, setActiveProject] = useState(null)
  const [presentations, setPresentations] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadThemes()
    loadPresentations()
  }, [])

  const loadThemes = async () => {
    try {
      const response = await api.getThemes()
      if (response.data.success) {
        setThemes(response.data.themes)
      }
    } catch (error) {
      console.error('Failed to load themes:', error)
    }
  }

  const loadPresentations = async () => {
    try {
      const response = await api.getProjects()
      if (response.data.success) {
        setPresentations(response.data.projects)
      }
    } catch (error) {
      console.error('Failed to load presentations:', error)
    }
  }

  const handleGeneratePresentation = async (formData) => {
    setIsLoading(true)
    try {
      const response = await api.generatePresentation({
        ...formData,
        theme: selectedTheme
      })
      
      if (response.data.success) {
        setActiveProject(response.data.project_id)
        await loadPresentations()
      }
    } catch (error) {
      console.error('Failed to generate presentation:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeletePresentation = async (projectId) => {
    try {
      await api.deleteProject(projectId)
      await loadPresentations()
      if (activeProject === projectId) {
        setActiveProject(null)
      }
    } catch (error) {
      console.error('Failed to delete presentation:', error)
    }
  }

  const handleDownloadPDF = async (projectId) => {
    try {
      const response = await api.downloadPDF(projectId)
      
      // Create blob and download
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `presentation_${projectId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download PDF:', error)
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50"></div>
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden">
          <div className="absolute -top-1/2 -right-1/2 w-96 h-96 bg-gradient-to-br from-blue-400/10 to-purple-600/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-1/2 -left-1/2 w-96 h-96 bg-gradient-to-tr from-purple-400/10 to-pink-600/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-indigo-400/5 to-cyan-600/5 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s'}}></div>
        </div>
      </div>

      <div className="relative z-10">
        <Header />
        
        <main className="container mx-auto px-6 py-8">
          <div className="max-w-7xl mx-auto">
            <Tabs defaultValue="generate" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="generate">✨ Generate Presentation</TabsTrigger>
                <TabsTrigger value="manage">📊 Manage Presentations</TabsTrigger>
              </TabsList>
              
              <TabsContent value="generate" className="space-y-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  <div className="lg:col-span-2">
                    <PresentationForm 
                      onSubmit={handleGeneratePresentation}
                      isLoading={isLoading}
                    />
                  </div>
                  <div>
                    <ThemeSelector 
                      themes={themes}
                      selectedTheme={selectedTheme}
                      onThemeChange={setSelectedTheme}
                    />
                  </div>
                </div>
                
                {activeProject && (
                  <GenerationStatus 
                    projectId={activeProject}
                    onComplete={() => {
                      loadPresentations()
                      setActiveProject(null)
                    }}
                    onDownload={handleDownloadPDF}
                  />
                )}
              </TabsContent>
              
              <TabsContent value="manage">
                <PresentationList 
                  presentations={presentations}
                  onDelete={handleDeletePresentation}
                  onDownload={handleDownloadPDF}
                  onRefresh={loadPresentations}
                />
              </TabsContent>
            </Tabs>
          </div>
        </main>
        
        <Footer />
      </div>
    </div>
  )
}

export default App
