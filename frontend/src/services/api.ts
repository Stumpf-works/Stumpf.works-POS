import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/authStore'

// API configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_VERSION = '/api/v1'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState()

    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }

    // Add tenant ID header (get from subdomain or config)
    const tenantId = getTenantId()
    if (tenantId) {
      config.headers['X-Tenant-ID'] = tenantId
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const { refreshToken, logout } = useAuthStore.getState()

      if (refreshToken) {
        try {
          const response = await axios.post(
            `${API_URL}${API_VERSION}/auth/refresh`,
            { refresh_token: refreshToken }
          )

          const { access_token, refresh_token } = response.data

          useAuthStore.getState().setTokens(access_token, refresh_token)

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          // Refresh failed, logout user
          logout()
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token, logout
        logout()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// Helper function to get tenant ID
function getTenantId(): string | null {
  // Try to get from subdomain
  const hostname = window.location.hostname
  const parts = hostname.split('.')

  // If subdomain exists (e.g., tenant1.example.com)
  if (parts.length >= 3) {
    return parts[0]
  }

  // Otherwise use from localStorage or default
  return localStorage.getItem('tenant_id') || null
}

// API methods
export const api = {
  // Generic methods
  get: <T = unknown>(url: string, config?: AxiosRequestConfig) =>
    apiClient.get<T>(url, config).then((res) => res.data),

  post: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    apiClient.post<T>(url, data, config).then((res) => res.data),

  put: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    apiClient.put<T>(url, data, config).then((res) => res.data),

  delete: <T = unknown>(url: string, config?: AxiosRequestConfig) =>
    apiClient.delete<T>(url, config).then((res) => res.data),

  // Auth endpoints
  auth: {
    login: (username_or_email: string, password: string) =>
      api.post('/auth/login', { username_or_email, password }),

    loginWithPIN: (pin_code: string) =>
      api.post('/auth/login/pin', { pin_code }),

    register: (data: Record<string, unknown>) => api.post('/auth/register', data),

    logout: () => api.post('/auth/logout'),

    me: () => api.get('/auth/me'),

    refresh: (refresh_token: string) =>
      api.post('/auth/refresh', { refresh_token }),
  },

  // Product endpoints
  products: {
    list: (params?: Record<string, unknown>) => api.get('/products', { params }),

    get: (id: number) => api.get(`/products/${id}`),

    create: (data: Record<string, unknown>) => api.post('/products', data),

    update: (id: number, data: Record<string, unknown>) => api.put(`/products/${id}`, data),

    delete: (id: number) => api.delete(`/products/${id}`),

    adjustStock: (id: number, quantity: number, reason?: string) =>
      api.post(`/products/${id}/stock`, { quantity, reason }),
  },

  // Product categories
  categories: {
    list: (params?: Record<string, unknown>) => api.get('/products/categories', { params }),

    get: (id: number) => api.get(`/products/categories/${id}`),

    create: (data: Record<string, unknown>) => api.post('/products/categories', data),

    update: (id: number, data: Record<string, unknown>) => api.put(`/products/categories/${id}`, data),

    delete: (id: number) => api.delete(`/products/categories/${id}`),
  },

  // Transaction endpoints
  transactions: {
    list: (params?: Record<string, unknown>) => api.get('/transactions', { params }),

    get: (id: number) => api.get(`/transactions/${id}`),

    create: (data: Record<string, unknown>) => api.post('/transactions', data),

    cancel: (id: number, reason?: string) =>
      api.post(`/transactions/${id}/cancel`, { reason }),

    stats: (params?: Record<string, unknown>) => api.get('/transactions/stats/summary', { params }),
  },
}

export default apiClient
