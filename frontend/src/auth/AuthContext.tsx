import { createContext, useCallback, useContext, useState } from 'react'
import type { ReactNode } from 'react'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

interface AuthContextValue {
  isAdmin: boolean
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue>({
  isAdmin: false,
  token: null,
  login: async () => {},
  logout: () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  // sessionStorage clears when the browser tab closes, so admin mode does not
  // persist across sessions on shared devices.
  const [token, setToken] = useState<string | null>(() =>
    sessionStorage.getItem('admin_token')
  )

  const login = useCallback(async (username: string, password: string) => {
    const resp = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!resp.ok) throw new Error('Invalid credentials')
    const data = await resp.json()
    sessionStorage.setItem('admin_token', data.access_token)
    setToken(data.access_token)
  }, [])

  const logout = useCallback(() => {
    sessionStorage.removeItem('admin_token')
    setToken(null)
  }, [])

  return (
    <AuthContext.Provider value={{ isAdmin: !!token, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
