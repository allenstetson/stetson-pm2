import { useEffect, useState } from 'react'
import { Box } from '@mui/material'
import { AuthProvider, useAuth } from './auth/AuthContext'
import { LoginModal } from './auth/LoginModal'
import { Header } from './components/layout/Header'
import { Sidebar, PageType } from './components/layout/Sidebar'
import { DetailsPanel } from './components/layout/DetailsPanel'
import { Footer } from './components/layout/Footer'
import { MainContent } from './components/panels/MainContent'
import { ProjectSummary } from './types/project'

// AppContent lives inside AuthProvider so it can call useAuth().
function AppContent() {
  const { isAdmin, logout } = useAuth()
  const [currentPage, setCurrentPage] = useState<PageType>('projects')
  const [selectedProject, setSelectedProject] = useState<ProjectSummary | null>(null)
  const [loginModalOpen, setLoginModalOpen] = useState(false)

  // Open login modal automatically when the admin navigates to the secret URL.
  // Replace the path immediately so it doesn't appear in browser history.
  useEffect(() => {
    const adminRoute = import.meta.env.VITE_ADMIN_ROUTE ?? '/admin-5e8a2b9f4c1d'
    if (window.location.pathname === adminRoute) {
      window.history.replaceState(null, '', '/')
      setLoginModalOpen(true)
    }
  }, [])

  // Ctrl+Shift+K (or Cmd+Shift+K on Mac): toggle admin mode.
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'K') {
        e.preventDefault()
        if (isAdmin) {
          logout()
        } else {
          setLoginModalOpen(true)
        }
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isAdmin, logout])

  const handleNavigate = (page: PageType) => {
    setCurrentPage(page)
    setSelectedProject(null)
  }

  const handleSelectProject = (project: ProjectSummary | null) => {
    setSelectedProject(project)
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <LoginModal open={loginModalOpen} onClose={() => setLoginModalOpen(false)} />
      <Header />

      <Box sx={{ display: 'flex', flex: 1 }}>
        <Sidebar currentPage={currentPage} onNavigate={handleNavigate} />
        <MainContent
          currentPage={currentPage}
          selectedProjectId={selectedProject?.id ?? null}
          onSelectProject={handleSelectProject}
        />
        <DetailsPanel selectedProject={selectedProject} />
      </Box>

      <Footer />
    </Box>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
