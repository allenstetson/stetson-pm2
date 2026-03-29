import { AppBar, IconButton, Toolbar, Tooltip, Typography } from '@mui/material'
import LockOpenIcon from '@mui/icons-material/LockOpen'
import { useAuth } from '../../auth/AuthContext'

export function Header() {
  const { isAdmin, logout } = useAuth()

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Stetson Home Projects Manager
        </Typography>
        {isAdmin && (
          <Tooltip title="Admin mode — click to sign out">
            <IconButton color="inherit" onClick={logout} size="small" aria-label="sign out">
              <LockOpenIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}
      </Toolbar>
    </AppBar>
  )
}
