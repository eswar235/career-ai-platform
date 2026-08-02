/**
 * API Client Configuration
 * Centralized axios instance for API calls
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import { getAccessToken, getRefreshToken, setTokens, removeTokens } from '@/lib/auth/storage'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIClient {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api`,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add token to request headers
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
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
                refresh_token: refreshToken,
              })

              const { access_token, refresh_token } = response.data
              setTokens(access_token, refresh_token)

              // Retry original request with new token
              originalRequest.headers.Authorization = `Bearer ${access_token}`
              return this.api(originalRequest)
            }
          } catch (err) {
            removeTokens()
            window.location.href = '/login'
          }
        }

        return Promise.reject(error)
      }
    )
  }

  get instance(): AxiosInstance {
    return this.api
  }

  async get<T>(url: string, config?: AxiosRequestConfig) {
    return this.api.get<T>(url, config)
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.api.post<T>(url, data, config)
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.api.put<T>(url, data, config)
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.api.patch<T>(url, data, config)
  }

  async delete<T>(url: string, config?: AxiosRequestConfig) {
    return this.api.delete<T>(url, config)
  }
}

export const apiClient = new APIClient()
