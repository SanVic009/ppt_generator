import axios from 'axios'

const BASE_URL = 'http://localhost:5000'

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  // Generate presentation
  generatePresentation: (data) => apiClient.post('/api/presentations', data),
  
  // Get themes
  getThemes: () => apiClient.get('/api/themes'),
  
  // Get projects
  getProjects: () => apiClient.get('/api/projects'),
  
  // Get project status
  getProjectStatus: (projectId) => apiClient.get(`/api/projects/${projectId}/status`),
  
  // Delete project
  deleteProject: (projectId) => apiClient.delete(`/api/projects/${projectId}`),
  
  // Download PDF
  downloadPDF: (projectId) => apiClient.get(`/api/presentations/${projectId}/download/pdf`, {
    responseType: 'blob'
  }),
  
  // Get API status
  getStatus: () => apiClient.get('/'),
}
