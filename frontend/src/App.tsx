import { useState } from 'react'
import { Box } from '@mui/material'
import { Header } from './components/layout/Header'
import { Sidebar, PageType } from './components/layout/Sidebar'
import { DetailsPanel } from './components/layout/DetailsPanel'
import { Footer } from './components/layout/Footer'
import { MainContent } from './components/panels/MainContent'

function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('projects')

  const handleNavigate = (page: PageType) => {
    setCurrentPage(page)
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />

      <Box sx={{ display: 'flex', flex: 1 }}>
        <Sidebar currentPage={currentPage} onNavigate={handleNavigate} />
        <MainContent currentPage={currentPage} />
        <DetailsPanel />
      </Box>

      <Footer />
    </Box>
  )
}

export default App
