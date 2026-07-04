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
};
