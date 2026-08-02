/**
 * Authentication-related type definitions
 */

export interface User {
  id: string
  email: string
  fullName?: string
  emailVerified: boolean
  isActive: boolean
  createdAt: string
  updatedAt: string
  lastLogin?: string
}

export interface TokenResponse {
  accessToken: string
  refreshToken: string
  tokenType: string
  expiresIn: number
}

export interface Tokens {
  accessToken: string
  refreshToken: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  fullName?: string
}

export interface AuthError {
  message: string
  code?: string
  status?: number
}
