// Confidence thresholds and display metadata
export const CONFIDENCE_LEVELS = {
  high: {
    label: "High",
    min: 0.85,
    colorClass: "text-confidence-high bg-confidence-high/10",
    badgeVariant: "high" as const,
  },
  medium: {
    label: "Medium",
    min: 0.6,
    colorClass: "text-confidence-med bg-confidence-med/10",
    badgeVariant: "medium" as const,
  },
  low: {
    label: "Low",
    min: 0,
    colorClass: "text-confidence-low bg-confidence-low/10",
    badgeVariant: "low" as const,
  },
} as const;

export type ConfidenceLevel = keyof typeof CONFIDENCE_LEVELS;

export function getConfidenceLevel(score: number): ConfidenceLevel {
  if (score >= CONFIDENCE_LEVELS.high.min) return "high";
  if (score >= CONFIDENCE_LEVELS.medium.min) return "medium";
  return "low";
}

export function formatConfidencePercent(score: number): string {
  return `${Math.round(score * 100)}%`;
}
