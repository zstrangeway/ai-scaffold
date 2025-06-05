import { SignInRequest, RegisterRequest, SignInResponse, RegisterResponse } from '@my-scaffold-project/api-contracts/generated/ts/gateway_service_pb';

// API base configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorText = await response.text();
        return {
          success: false,
          error: errorText || `HTTP error! status: ${response.status}`,
        };
      }

      const data = await response.json();
      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
      };
    }
  }

  async signIn(email: string, password: string): Promise<ApiResponse<any>> {
    const request = new SignInRequest({
      email,
      password,
    });

    return this.makeRequest('/api/v1/auth/signin', {
      method: 'POST',
      body: JSON.stringify({
        email: request.email,
        password: request.password,
      }),
    });
  }

  async register(name: string, email: string, password: string): Promise<ApiResponse<any>> {
    const request = new RegisterRequest({
      name,
      email,
      password,
    });

    return this.makeRequest('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        name: request.name,
        email: request.email,
        password: request.password,
      }),
    });
  }

  async validateToken(token: string): Promise<ApiResponse<any>> {
    return this.makeRequest('/api/v1/auth/validate', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async refreshToken(refreshToken: string): Promise<ApiResponse<any>> {
    return this.makeRequest('/api/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }
}

export const apiClient = new ApiClient();
export default apiClient;