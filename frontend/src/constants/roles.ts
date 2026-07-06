export const ROLES = {
  admin: "admin",
  physician: "physician",
  patient: "patient",
} as const;

export type Role = (typeof ROLES)[keyof typeof ROLES];
