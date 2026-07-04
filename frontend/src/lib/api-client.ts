/**
 * API Client Foundation for AarogyaAgent v2 Backend.
 *
 * Provides typed fetch wrappers with automatic base URL injection,
 * JWT Authorization header injection, cancellation support (AbortSignal),
 * retry logic, and structured error handling.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  public code: string;
  public status: number;
  public details?: unknown;

  constructor(status: number, message: string, code = "UNKNOWN_ERROR", details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

// Global hook/store for token access (will be populated by AuthProvider)
let getAuthToken: () => string | null = () => null;

export const setTokenProvider = (provider: () => string | null) => {
  getAuthToken = provider;
};

interface FetchOptions extends RequestInit {
  retries?: number;
}

async function fetchWithRetry(url: string, options: FetchOptions): Promise<Response> {
  let { retries = 1, ...fetchOptions } = options;
  let response: Response | undefined;
  
  while (retries >= 0) {
    try {
      response = await fetch(url, fetchOptions);
      if (response.ok || response.status < 500) {
        return response; // Return immediately if successful or if it's a client error (4xx)
      }
    } catch (error) {
      if (retries === 0 || (error instanceof DOMException && error.name === "AbortError")) {
        throw error;
      }
    }
    retries--;
    if (retries >= 0) {
      await new Promise(res => setTimeout(res, 1000)); // basic 1s backoff
    }
  }
  
  if (!response) {
    throw new Error("Network error");
  }
  return response;
}

async function handleResponse<T>(response: Response): Promise<T> {
  const isJson = response.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    // Structured error schema from backend: { error_code, message, correlation_id, timestamp, details }
    const errorData = data && typeof data === "object" ? (data as Record<string, unknown>) : null;
    const message = (errorData && typeof errorData.message === "string") ? errorData.message : response.statusText;
    const code = (errorData && typeof errorData.error_code === "string") ? errorData.error_code : "HTTP_ERROR";
    const details = errorData ? errorData.details : undefined;
    
    // Global interceptor logic can be placed here (e.g. redirect to login on 401)
    if (response.status === 401 && typeof window !== "undefined") {
        // We could dispatch an event or redirect to login here
        window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    }

    throw new ApiError(response.status, message, code, details);
  }

  return data as T;
}

function getHeaders(customHeaders?: HeadersInit): Headers {
  const headers = new Headers(customHeaders);
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const token = getAuthToken();
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return headers;
}

export const apiClient = {
  async get<T>(path: string, options: FetchOptions = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`;
    const response = await fetchWithRetry(url, {
      ...options,
      method: "GET",
      headers: getHeaders(options.headers),
    });
    return handleResponse<T>(response);
  },

  async post<T>(path: string, body?: unknown, options: FetchOptions = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`;
    const response = await fetchWithRetry(url, {
      ...options,
      method: "POST",
      headers: getHeaders(options.headers),
      body: body ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async put<T>(path: string, body?: unknown, options: FetchOptions = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`;
    const response = await fetchWithRetry(url, {
      ...options,
      method: "PUT",
      headers: getHeaders(options.headers),
      body: body ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async delete<T>(path: string, options: FetchOptions = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`;
    const response = await fetchWithRetry(url, {
      ...options,
      method: "DELETE",
      headers: getHeaders(options.headers),
    });
    return handleResponse<T>(response);
  },

  /**
   * Future-ready Server-Sent Events (SSE) connector.
   */
  createEventSource(path: string): EventSource {
    const url = `${API_BASE_URL}${path}`;
    // Note: Native EventSource doesn't support custom headers (like Authorization) easily.
    // We append the token to the URL or we use a library like @microsoft/fetch-event-source
    const token = getAuthToken();
    const finalUrl = token ? `${url}?token=${token}` : url;
    return new EventSource(finalUrl);
  },

  /**
   * Future-ready WebSocket connector.
   */
  createWebSocket(path: string): WebSocket {
    const wsUrl = API_BASE_URL.replace(/^http/, "ws") + path;
    const token = getAuthToken();
    const finalUrl = token ? `${wsUrl}?token=${token}` : wsUrl;
    return new WebSocket(finalUrl);
  }
};
