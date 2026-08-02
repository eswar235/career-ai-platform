/**
 * Secure token storage utilities
 * Uses localStorage with careful handling for SSR compatibility
 */

import { Tokens } from './types'

const ACCESS_TOKEN_KEY = 'career_ai_access_token'
const REFRESH_TOKEN_KEY = 'career_ai_refresh_token'

/**
 * Check if we're in a browser environment
 */
function isBrowser(): boolean {
  return typeof window !== 'undefined'
}

/**
 * Store tokens in localStorage
 */
export function setTokens(accessToken: string, refreshToken: string): void {
  if (!isBrowser()) return

  try {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  } catch (error) {
    console.error('Failed to store tokens:', error)
  }
}

/**
 * Retrieve tokens from localStorage
 */
export function getTokens(): Tokens | null {
  if (!isBrowser()) return null

  try {
    const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

    if (accessToken && refreshToken) {
      return { accessToken, refreshToken }
    }
    return null
  } catch (error) {
    console.error('Failed to retrieve tokens:', error)
    return null
  }
}

/**
 * Get access token
 */
export function getAccessToken(): string | null {
  if (!isBrowser()) return null

  try {
    return localStorage.getItem(ACCESS_TOKEN_KEY)
  } catch (error) {
    console.error('Failed to retrieve access token:', error)
    return null
  }
}

/**
 * Get refresh token
 */
export function getRefreshToken(): string | null {
  if (!isBrowser()) return null

  try {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  } catch (error) {
    console.error('Failed to retrieve refresh token:', error)
    return null
  }
}

/**
 * Remove tokens from storage
 */
export function removeTokens(): void {
  if (!isBrowser()) return

  try {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  } catch (error) {
    console.error('Failed to remove tokens:', error)
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const tokens = getTokens()
  return !!tokens?.accessToken
}

/**
 * Get current user from session storage (cached)
 */
export function getCurrentUser(): any {
  if (!isBrowser()) return null

  try {
    const userStr = sessionStorage.getItem('career_ai_current_user')
    return userStr ? JSON.parse(userStr) : null
  } catch (error) {
    console.error('Failed to retrieve current user:', error)
    return null
  }
}

/**
 * Store current user in session storage
 */
export function setCurrentUser(user: any): void {
  if (!isBrowser()) return

  try {
    sessionStorage.setItem('career_ai_current_user', JSON.stringify(user))
  } catch (error) {
    console.error('Failed to store current user:', error)
  }
}

/**
 * Clear current user
 */
export function clearCurrentUser(): void {
  if (!isBrowser()) return

  try {
    sessionStorage.removeItem('career_ai_current_user')
  } catch (error) {
    console.error('Failed to clear current user:', error)
  }
}
