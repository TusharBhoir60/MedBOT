"use client";

import { MetricCard as BaseMetricCard } from "@/components/domain/metric-card";
import { LucideIcon } from "lucide-react";

interface AnalyticsMetricCardProps {
  label: string;
  value: number | string | null;
  description?: string;
  icon?: LucideIcon;
  format?: "number" | "percent" | "duration" | "text";
  className?: string;
}

export function AnalyticsMetricCard({
  label,
  value,
  description,
  icon,
  format = "number",
  className,
}: AnalyticsMetricCardProps) {
  let displayValue: string;

  if (value === null || value === undefined) {
    displayValue = "N/A";
  } else if (format === "percent" && typeof value === "number") {
    displayValue = `${(value * 100).toFixed(1)}%`;
  } else if (format === "duration" && typeof value === "number") {
    // Duration in seconds -> format to readable
    if (value < 60) displayValue = `${Math.round(value)}s`;
    else if (value < 3600) displayValue = `${Math.round(value / 60)}m`;
    else displayValue = `${(value / 3600).toFixed(1)}h`;
  } else if (format === "number" && typeof value === "number") {
    displayValue = new Intl.NumberFormat().format(value);
  } else {
    displayValue = String(value);
  }

  return (
    <BaseMetricCard
      label={label}
      value={displayValue}
      description={description}
      icon={icon}
      className={className}
    />
  );
}
