// Medical severity levels and display metadata
export const SEVERITY_LEVELS = {
  critical: {
    label: "Critical",
    description: "Requires immediate emergency care",
    colorClass: "text-severity-critical bg-severity-critical/10",
    badgeVariant: "critical" as const,
  },
  high: {
    label: "High",
    description: "Requires urgent medical attention",
    colorClass: "text-severity-high bg-severity-high/10",
    badgeVariant: "high" as const,
  },
  medium: {
    label: "Medium",
    description: "Should be seen by a doctor soon",
    colorClass: "text-severity-medium bg-severity-medium/10",
    badgeVariant: "medium" as const,
  },
  low: {
    label: "Low",
    description: "Monitor symptoms; may self-treat",
    colorClass: "text-severity-low bg-severity-low/10",
    badgeVariant: "low" as const,
  },
} as const;

export type SeverityLevel = keyof typeof SEVERITY_LEVELS;
