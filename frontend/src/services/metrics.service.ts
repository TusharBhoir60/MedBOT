import { apiClient } from "@/lib/api-client";
import {
  MetricsOverviewSchema,
  MetricsOverview,
  ConfidenceMetricsSchema,
  ConfidenceMetrics,
  ReviewMetricsSchema,
  ReviewMetrics,
  ClinicalMetricsSchema,
  ClinicalMetrics,
  ActivityFeedSchema,
  ActivityFeed,
  SystemMetricsSchema,
  SystemMetrics,
} from "@/schemas/metrics.schema";

export interface MetricsFilters {
  startDate?: string;
  endDate?: string;
}

export interface ActivityFilters {
  limit?: number;
  cursor?: string;
}

/**
 * Helper to build query parameters for metrics.
 */
function buildQueryString(filters?: MetricsFilters | ActivityFilters): string {
  if (!filters) return "";
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== "") {
      // In JS APIs, snake_case is expected by the backend for query params in this project?
      // Wait, let's check backend router_metrics.py from Sprint 8A:
      // It expects start_date and end_date. Let's map them.
      const paramKey = key === "startDate" ? "start_date" : key === "endDate" ? "end_date" : key;
      params.append(paramKey, String(value));
    }
  }
  const str = params.toString();
  return str ? `?${str}` : "";
}

export const metricsService = {
  getOverview: async (filters?: MetricsFilters, signal?: AbortSignal): Promise<MetricsOverview> => {
    const qs = buildQueryString(filters);
    const data = await apiClient.get<unknown>(`/api/v1/metrics/overview${qs}`, { signal });
    return MetricsOverviewSchema.parse(data);
  },

  getConfidenceMetrics: async (filters?: MetricsFilters, signal?: AbortSignal): Promise<ConfidenceMetrics> => {
    const qs = buildQueryString(filters);
    const data = await apiClient.get<unknown>(`/api/v1/metrics/confidence${qs}`, { signal });
    return ConfidenceMetricsSchema.parse(data);
  },

  getReviewMetrics: async (filters?: MetricsFilters, signal?: AbortSignal): Promise<ReviewMetrics> => {
    const qs = buildQueryString(filters);
    const data = await apiClient.get<unknown>(`/api/v1/metrics/reviews${qs}`, { signal });
    return ReviewMetricsSchema.parse(data);
  },

  getClinicalMetrics: async (filters?: MetricsFilters, signal?: AbortSignal): Promise<ClinicalMetrics> => {
    const qs = buildQueryString(filters);
    const data = await apiClient.get<unknown>(`/api/v1/metrics/clinical${qs}`, { signal });
    return ClinicalMetricsSchema.parse(data);
  },

  getActivity: async (filters?: ActivityFilters, signal?: AbortSignal): Promise<ActivityFeed> => {
    const qs = buildQueryString(filters);
    const data = await apiClient.get<unknown>(`/api/v1/metrics/activity${qs}`, { signal });
    return ActivityFeedSchema.parse(data);
  },

  getSystemMetrics: async (signal?: AbortSignal): Promise<SystemMetrics> => {
    const data = await apiClient.get<unknown>(`/api/v1/metrics/system`, { signal });
    return SystemMetricsSchema.parse(data);
  },
};
