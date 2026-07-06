"use client";

import { cn } from "@/lib/utils";
import {
  getConfidenceLevel,
  formatConfidencePercent,
  CONFIDENCE_LEVELS,
} from "@/constants/confidence";
import {
  SEVERITY_LEVELS,
  type SeverityLevel,
} from "@/constants/severity";
import { REVIEW_STATUS_COLORS, REVIEW_STATUS_LABELS } from "@/constants/review";

// ---------------------------------------------------------------------------
// ConfidenceBadge
// ---------------------------------------------------------------------------
interface ConfidenceBadgeProps {
  score: number;
  className?: string;
}

export function ConfidenceBadge({ score, className }: ConfidenceBadgeProps) {
  const level = getConfidenceLevel(score);
  const meta = CONFIDENCE_LEVELS[level];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
        meta.colorClass,
        className
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {meta.label} · {formatConfidencePercent(score)}
    </span>
  );
}

// ---------------------------------------------------------------------------
// SeverityBadge
// ---------------------------------------------------------------------------
interface SeverityBadgeProps {
  level: SeverityLevel;
  className?: string;
}

export function SeverityBadge({ level, className }: SeverityBadgeProps) {
  const meta = SEVERITY_LEVELS[level];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
        meta.colorClass,
        className
      )}
      title={meta.description}
    >
      {meta.label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// StatusBadge
// ---------------------------------------------------------------------------
interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const colorClass = REVIEW_STATUS_COLORS[status] ?? "bg-muted text-muted-foreground";
  const label = REVIEW_STATUS_LABELS[status] ?? status;
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        colorClass,
        className
      )}
    >
      {label}
    </span>
  );
}
