import { useQuery } from "@tanstack/react-query";
import { metricsService, MetricsFilters, ActivityFilters } from "@/services/metrics.service";

export const metricsKeys = {
  all: ["metrics"] as const,
  overview: (filters?: MetricsFilters) => [...metricsKeys.all, "overview", filters] as const,
  confidence: (filters?: MetricsFilters) => [...metricsKeys.all, "confidence", filters] as const,
  reviews: (filters?: MetricsFilters) => [...metricsKeys.all, "reviews", filters] as const,
  clinical: (filters?: MetricsFilters) => [...metricsKeys.all, "clinical", filters] as const,
  activity: (filters?: ActivityFilters) => [...metricsKeys.all, "activity", filters] as const,
  system: () => [...metricsKeys.all, "system"] as const,
};

const AGGREGATE_STALE_TIME = 60 * 1000; // 60 seconds
const SYSTEM_STALE_TIME = 15 * 1000; // 15 seconds
const ACTIVITY_STALE_TIME = 30 * 1000; // 30 seconds

export function useMetricsOverview(filters?: MetricsFilters) {
  return useQuery({
    queryKey: metricsKeys.overview(filters),
    queryFn: ({ signal }) => metricsService.getOverview(filters, signal),
    staleTime: AGGREGATE_STALE_TIME,
    refetchOnWindowFocus: true,
  });
}

export function useConfidenceMetrics(filters?: MetricsFilters) {
  return useQuery({
    queryKey: metricsKeys.confidence(filters),
    queryFn: ({ signal }) => metricsService.getConfidenceMetrics(filters, signal),
    staleTime: AGGREGATE_STALE_TIME,
    refetchOnWindowFocus: true,
  });
}

export function useReviewMetrics(filters?: MetricsFilters) {
  return useQuery({
    queryKey: metricsKeys.reviews(filters),
    queryFn: ({ signal }) => metricsService.getReviewMetrics(filters, signal),
    staleTime: AGGREGATE_STALE_TIME,
    refetchOnWindowFocus: true,
  });
}

export function useClinicalMetrics(filters?: MetricsFilters) {
  return useQuery({
    queryKey: metricsKeys.clinical(filters),
    queryFn: ({ signal }) => metricsService.getClinicalMetrics(filters, signal),
    staleTime: AGGREGATE_STALE_TIME,
    refetchOnWindowFocus: true,
  });
}

export function useMetricsActivity(filters?: ActivityFilters) {
  return useQuery({
    queryKey: metricsKeys.activity(filters),
    queryFn: ({ signal }) => metricsService.getActivity(filters, signal),
    staleTime: ACTIVITY_STALE_TIME,
    refetchOnWindowFocus: true,
  });
}

export function useSystemMetrics() {
  return useQuery({
    queryKey: metricsKeys.system(),
    queryFn: ({ signal }) => metricsService.getSystemMetrics(signal),
    staleTime: SYSTEM_STALE_TIME,
    refetchOnWindowFocus: true,
  });
}
