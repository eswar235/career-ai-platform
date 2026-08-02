/**
 * Authentication API client
 */

import axios, { AxiosInstance } from 'axios'

import { User, TokenResponse, LoginRequest, RegisterRequest } from '@/lib/auth/types'
import { getAccessToken, getRefreshToken, setTokens, removeTokens } from '@/lib/auth/storage'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class AuthAPI {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api/auth`,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add token to requests
    this.api.interceptors.request.use((config) => {
      const token = getAccessToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Handle token refresh on 401
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const refreshToken = getRefreshToken()
            if (!refreshToken) {
              removeTokens()
              window.location.href = '/login'
              return Promise.reject(error)
            }

            const response = await this.api.post('/refresh', {
              refresh_token: refreshToken,
            })

            const { access_token, refresh_token } = response.data
            setTokens(access_token, refresh_token)

            // Retry original request
            originalRequest.headers.Authorization = `Bearer ${access_token}`
            return this.api(originalRequest)
          } catch (refreshError) {
            removeTokens()
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  /**
   * Register a new user
   */
  async register(
    email: string,
    password: string,
    fullName?: string
  ): Promise<User> {
    const response = await this.api.post('/register', {
      email,
      password,
      full_name: fullName,
    })
    return response.data
  }

  /**
   * Login user
   */
  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await this.api.post('/login', {
      email,
      password,
    } as LoginRequest)
    return {
      accessToken: response.data.access_token,
      refreshToken: response.data.refresh_token,
      tokenType: response.data.token_type,
      expiresIn: response.data.expires_in,
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await this.api.post('/refresh', {
      refresh_token: refreshToken,
    })
    return {
      accessToken: response.data.access_token,
      refreshToken: response.data.refresh_token,
      tokenType: response.data.token_type,
      expiresIn: response.data.expires_in,
    }
  }

  /**
   * Get current user
   */
  async getCurrentUser(token: string): Promise<User> {
    const response = await this.api.get('/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    return response.data
  }

  /**
   * Logout user
   */
  async logout(token: string): Promise<void> {
    await this.api.post(
      '/logout',
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )
  }
}

export const authAPI = new AuthAPI()
