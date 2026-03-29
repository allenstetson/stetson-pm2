import { Box, Paper, Typography } from '@mui/material'
import { PageType } from '../layout/Sidebar'
import { ProjectList } from '../projects/ProjectList'
import { ProjectSummary } from '../../types/project'

interface MainContentProps {
  currentPage: PageType
  selectedProjectId: string | null
  onSelectProject: (project: ProjectSummary | null) => void
}

const PAGE_CONTENT: Record<PageType, { title: string; description: string }> =
  {
    dashboard: {
      title: 'Dashboard',
      description: 'Welcome to Stetson Home Projects Manager',
    },
    projects: {
      title: 'Projects',
      description: 'Projects list will appear here (with data from API)',
    },
    search: {
      title: 'Search',
      description: 'Search interface coming soon',
    },
    settings: {
      title: 'Settings',
      description: 'Settings panel coming soon',
    },
  }

export function MainContent({ currentPage, selectedProjectId, onSelectProject }: MainContentProps) {
  const content = PAGE_CONTENT[currentPage]

  return (
    <Box sx={{ flex: 1, p: 3, backgroundColor: '#f5f5f5', overflowY: 'auto' }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          {content.title}
        </Typography>
        {currentPage === 'projects' ? (
          <ProjectList
            selectedProjectId={selectedProjectId}
            onSelectProject={onSelectProject}
          />
        ) : (
          <Typography variant="body2" color="textSecondary">
            {content.description}
          </Typography>
        )}
      </Paper>
    </Box>
  )
}
