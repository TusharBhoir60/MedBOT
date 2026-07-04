import { apiClient } from "@/lib/api-client";
import { HealthResponse } from "@/schemas/health.schema";

export const healthService = {
  getOverall: async (): Promise<HealthResponse> => {
    return apiClient.get<HealthResponse>("/api/v1/health");
  },

  getLiveness: async (): Promise<{ status: string }> => {
    return apiClient.get<{ status: string }>("/api/v1/health/live");
  },

  getReadiness: async (): Promise<{ status: string }> => {
    return apiClient.get<{ status: string }>("/api/v1/health/ready");
  },
};
