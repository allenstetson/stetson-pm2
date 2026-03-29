import { useState } from 'react'
import {
  Alert,
  Button,
  Dialog,
  DialogContent,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import LockIcon from '@mui/icons-material/Lock'
import { useAuth } from './AuthContext'

interface LoginModalProps {
  open: boolean
  onClose: () => void
}

export function LoginModal({ open, onClose }: LoginModalProps) {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login(username, password)
      setUsername('')
      setPassword('')
      onClose()
    } catch {
      setError('Authentication failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogContent>
        <Stack component="form" onSubmit={handleSubmit} spacing={2} sx={{ pt: 1 }}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <LockIcon color="action" fontSize="small" />
            <Typography variant="subtitle2">Authentication Required</Typography>
          </Stack>

          {error && (
            <Alert severity="error" sx={{ py: 0.5 }}>
              {error}
            </Alert>
          )}

          <TextField
            label="Username"
            size="small"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
            autoComplete="username"
          />
          <TextField
            label="Password"
            type="password"
            size="small"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </Button>
        </Stack>
      </DialogContent>
    </Dialog>
  )
}
