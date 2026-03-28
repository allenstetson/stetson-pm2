import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  Paper,
} from '@mui/material'
import './App.css'

const DRAWER_WIDTH = 240

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Home Projects Manager
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box sx={{ display: 'flex', flex: 1 }}>
        {/* Left Navigation */}
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
            <Typography variant="body2" sx={{ mb: 1, cursor: 'pointer' }}>
              Dashboard
            </Typography>
            <Typography variant="body2" sx={{ mb: 1, cursor: 'pointer' }}>
              Projects
            </Typography>
            <Typography variant="body2" sx={{ mb: 1, cursor: 'pointer' }}>
              Search
            </Typography>
            <Typography variant="body2" sx={{ cursor: 'pointer' }}>
              Settings
            </Typography>
          </Box>
        </Drawer>

        {/* Center Content */}
        <Box sx={{ flex: 1, p: 3, backgroundColor: '#f5f5f5' }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" sx={{ mb: 2 }}>
              Projects
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Project list will appear here
            </Typography>
          </Paper>
        </Box>

        {/* Right Details Panel */}
        <Paper
          sx={{
            width: 300,
            flexShrink: 0,
            p: 2,
            marginTop: '64px',
            borderLeft: '1px solid #ddd',
          }}
        >
          <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
            Project Details
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Select a project to view details
          </Typography>
        </Paper>
      </Box>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 2,
          px: 3,
          backgroundColor: '#f5f5f5',
          borderTop: '1px solid #ddd',
        }}
      >
        <Typography variant="caption" color="textSecondary">
          Home Projects Manager v0.1.0
        </Typography>
      </Box>
    </Box>
  )
}

export default App
