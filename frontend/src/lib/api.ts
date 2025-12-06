// API Client for Backend Communication

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface ApiResponse<T> {
  data: T
  meta?: {
    timestamp: string
    total?: number
    page?: number
    page_size?: number
  }
}

export interface ApiError {
  error: {
    code: string
    message: string
  }
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`

    const defaultHeaders: HeadersInit = {
      'Content-Type': 'application/json',
    }

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
      credentials: 'include', // Send cookies with requests
    }

    try {
      const response = await fetch(url, config)

      // Handle 401 Unauthorized
      if (response.status === 401) {
        // Trigger logout via custom event
        window.dispatchEvent(new CustomEvent('auth:unauthorized'))
        throw new Error('Unauthorized')
      }

      if (!response.ok) {
        const errorData = await response.json()
        // Handle both FastAPI HTTPException format (detail) and custom error format (error)
        const message =
          errorData.error?.message ||
          errorData.detail?.message ||
          (typeof errorData.detail === 'string' ? errorData.detail : null) ||
          'Request failed'
        throw new Error(message)
      }

      const responseData = await response.json()

      // If the response already has a 'data' property, return as-is
      // Otherwise, wrap the response in a {data: ...} structure
      if ('data' in responseData) {
        return responseData
      }
      return { data: responseData }
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error('Unknown error occurred')
    }
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  async post<T, D = unknown>(endpoint: string, data?: D): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T, D = unknown>(endpoint: string, data?: D): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

// Singleton instance
export const apiClient = new ApiClient(API_BASE_URL)

export default apiClient
