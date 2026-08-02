/**
 * Custom hook for authentication state management
 */

import { useCallback, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

import { authAPI } from '@/lib/api/auth'
import { getCurrentUser, getTokens, setTokens, removeTokens } from '@/lib/auth/storage'
import { User } from '@/lib/auth/types'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  error: string | null
}

export function useAuth(): AuthContextType {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Initialize user from storage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setIsLoading(true)
        const tokens = getTokens()

        if (tokens?.accessToken) {
          // Try to get current user
          const currentUser = await authAPI.getCurrentUser(tokens.accessToken)
          setUser(currentUser)
        } else {
          setUser(null)
        }
      } catch (err) {
        // Clear invalid tokens
        removeTokens()
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    initializeAuth()
  }, [])

  const login = useCallback(
    async (email: string, password: string) => {
      try {
        setError(null)
        setIsLoading(true)

        const response = await authAPI.login(email, password)
        setTokens(response.accessToken, response.refreshToken)

        // Get user data
        const currentUser = await authAPI.getCurrentUser(response.accessToken)
        setUser(currentUser)

        router.push('/dashboard')
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Login failed'
        setError(message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [router]
  )

  const register = useCallback(
    async (email: string, password: string, fullName?: string) => {
      try {
        setError(null)
        setIsLoading(true)

        await authAPI.register(email, password, fullName)

        // Auto-login after registration
        await login(email, password)
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Registration failed'
        setError(message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [login]
  )

  const logout = useCallback(async () => {
    try {
      setError(null)
      const tokens = getTokens()

      if (tokens?.accessToken) {
        await authAPI.logout(tokens.accessToken)
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      removeTokens()
      setUser(null)
      router.push('/')
    }
  }, [router])

  const refreshToken = useCallback(async () => {
    try {
      const tokens = getTokens()
      if (!tokens?.refreshToken) {
        throw new Error('No refresh token available')
      }

      const response = await authAPI.refreshToken(tokens.refreshToken)
      setTokens(response.accessToken, response.refreshToken)
    } catch (err) {
      removeTokens()
      setUser(null)
      throw err
    }
  }, [])

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshToken,
    error,
  }
}
