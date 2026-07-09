export const ROUTES = {
  // Public
  home: "/",

  // Auth
  login: "/auth/login",

  // Patient
  chat: "/chat",

  // Physician
  dashboard: "/dashboard",
  dashboardTask: (id: string) => `/dashboard/task/${id}`,
  analytics: "/dashboard/analytics",
  analyticsPerformance: "/dashboard/analytics/performance",
  analyticsReview: "/dashboard/analytics/review",
  systemHealth: "/dashboard/system",
  observability: "/dashboard/observability",

  // Admin (future)
  admin: "/admin",
} as const;
