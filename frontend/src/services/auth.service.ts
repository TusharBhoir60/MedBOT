import { apiClient } from "@/lib/api-client";
import { LoginRequest, TokenResponse } from "@/schemas/auth.schema";

export const authService = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    // Note: The backend expects URL-encoded form data for OAuth2
    const params = new URLSearchParams();
    params.append("username", data.username);
    params.append("password", data.password);

    return apiClient.post<TokenResponse>("/api/v1/auth/login", undefined, {
      body: params,
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
  },

  register: async (data: LoginRequest): Promise<{ message: string }> => {
    return apiClient.post<{ message: string }>("/api/v1/auth/register", data);
  },

  forgotPassword: async (username: string): Promise<{ message: string; reset_token?: string }> => {
    return apiClient.post<{ message: string; reset_token?: string }>("/api/v1/auth/forgot-password", { username });
  },

  resetPassword: async (token: string, new_password: string): Promise<{ message: string }> => {
    return apiClient.post<{ message: string }>("/api/v1/auth/reset-password", { token, new_password });
  },
};
