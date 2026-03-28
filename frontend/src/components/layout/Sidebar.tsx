import { Box, Drawer, Typography } from '@mui/material'

export type PageType = 'dashboard' | 'projects' | 'search' | 'settings'

interface SidebarProps {
  currentPage: PageType
  onNavigate: (page: PageType) => void
}

const DRAWER_WIDTH = 240

const NAV_ITEMS: Array<{ label: string; page: PageType }> = [
  { label: 'Dashboard', page: 'dashboard' },
  { label: 'Projects', page: 'projects' },
  { label: 'Search', page: 'search' },
  { label: 'Settings', page: 'settings' },
]

export function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          marginTop: '64px',
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
          Navigation
        </Typography>
        {NAV_ITEMS.map((item) => (
          <Typography
            key={item.page}
            variant="body2"
            sx={{
              mb: 1,
              cursor: 'pointer',
              fontWeight: currentPage === item.page ? 'bold' : 'normal',
              color: currentPage === item.page ? 'primary.main' : 'inherit',
              '&:hover': {
                backgroundColor: '#f0f0f0',
                borderRadius: 1,
                pl: 1,
              },
              transition: 'all 0.2s ease',
              p: 1,
            }}
            onClick={() => onNavigate(item.page)}
          >
            {item.label}
          </Typography>
        ))}
      </Box>
    </Drawer>
  )
}
