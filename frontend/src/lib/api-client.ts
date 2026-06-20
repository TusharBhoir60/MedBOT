/**
 * API Client for AarogyaAgent v2 Backend.
 *
 * Provides typed fetch wrappers with automatic base URL injection
 * and error handling. Uses standard browser fetch API.
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

async function handleResponse<T>(response: Response): Promise<T> {
  const isJson = response.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const errorData = data && typeof data === "object" ? (data as Record<string, unknown>) : null;
    const message = (errorData && typeof errorData.message === "string") ? errorData.message : response.statusText;
    const code = (errorData && typeof errorData.error_code === "string") ? errorData.error_code : "HTTP_ERROR";
    const details = errorData ? errorData.details : undefined;
    throw new ApiError(response.status, message, code, details);
  }

  return data as T;
}

export const apiClient = {
  async get<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`;
    const response = await fetch(url, {
      ...options,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
    return handleResponse<T>(response);
  },

  async post<T>(path: string, body: unknown, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`;
    const response = await fetch(url, {
      ...options,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      body: JSON.stringify(body),
    });
    return handleResponse<T>(response);
  },

  async put<T>(path: string, body: unknown, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`;
    const response = await fetch(url, {
      ...options,
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      body: JSON.stringify(body),
    });
    return handleResponse<T>(response);
  },

  async delete<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`;
    const response = await fetch(url, {
      ...options,
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
    return handleResponse<T>(response);
  },
};
