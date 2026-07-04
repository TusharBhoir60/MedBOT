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

  // Admin (future)
  admin: "/admin",
} as const;
