import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

/** Same base as API_BASE_URL, but as a ws(s):// URL for the Duel Arena
 * socket -- http(s) doesn't apply to a WebSocket upgrade. When
 * VITE_API_URL is unset (local dev), API_BASE_URL is the relative '/api'
 * that Vite's dev server proxies (see vite.config.ts, which also needs
 * `ws: true` on that proxy entry for this to actually reach the backend),
 * so the socket has to be built from the current page's own origin
 * instead of being resolvable as a URL on its own. */
export function getWsBaseUrl(): string {
  if (API_BASE_URL.startsWith('http')) {
    return API_BASE_URL.replace(/^http/, 'ws');
  }
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${wsProtocol}//${window.location.host}${API_BASE_URL}`;
}

/** Read once by the Login page to show why the user landed there, instead of a silent redirect. */
export const AUTH_NOTICE_KEY = 'atlas_auth_notice';
const DISABLED_ACCOUNT_DETAIL = 'This account has been disabled';

class ApiClient {
  private client: AxiosInstance;
  private refreshTokenPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('access_token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        if (
          error.response?.status === 403 &&
          (error.response.data as { detail?: string } | undefined)?.detail === DISABLED_ACCOUNT_DETAIL
        ) {
          localStorage.removeItem('access_token');
          sessionStorage.setItem(AUTH_NOTICE_KEY, DISABLED_ACCOUNT_DETAIL);
          window.location.href = '/login';
          return Promise.reject(error);
        }

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const token = await this.refreshToken();
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return this.client(originalRequest);
          } catch {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
            return Promise.reject(error);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private async refreshToken(): Promise<string> {
    if (this.refreshTokenPromise) {
      return this.refreshTokenPromise;
    }

    this.refreshTokenPromise = (async () => {
      const response = await this.client.post('/auth/refresh', {}, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      const { access_token } = response.data;
      localStorage.setItem('access_token', access_token);
      return access_token;
    })();

    try {
      return await this.refreshTokenPromise;
    } finally {
      this.refreshTokenPromise = null;
    }
  }

  async get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    const response = await this.client.get<T>(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }

  async patch<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.patch<T>(url, data);
    return response.data;
  }

  async delete<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.delete<T>(url, { data });
    return response.data;
  }

  setAuthToken(token: string | null) {
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }
}

export const apiClient = new ApiClient();