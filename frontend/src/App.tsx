import { useState } from 'react'
import { Box } from '@mui/material'
import { Header } from './components/layout/Header'
import { Sidebar, PageType } from './components/layout/Sidebar'
import { DetailsPanel } from './components/layout/DetailsPanel'
import { Footer } from './components/layout/Footer'
import { MainContent } from './components/panels/MainContent'
import { ProjectSummary } from './types/project'

function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('projects')
  const [selectedProject, setSelectedProject] = useState<ProjectSummary | null>(null)

  const handleNavigate = (page: PageType) => {
    setCurrentPage(page)
    setSelectedProject(null)
  }

  const handleSelectProject = (project: ProjectSummary | null) => {
    setSelectedProject(project)
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
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

export default App
