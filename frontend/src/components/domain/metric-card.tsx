"use client";

import { cn } from "@/lib/utils";
import { LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  description?: string;
  icon?: LucideIcon;
  trend?: "up" | "down" | "flat";
  trendValue?: string;
  className?: string;
}

export function MetricCard({
  label,
  value,
  description,
  icon: Icon,
  trend,
  trendValue,
  className,
}: MetricCardProps) {
  const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;
  const trendColor =
    trend === "up" ? "text-success" : trend === "down" ? "text-error" : "text-muted-foreground";

  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-card p-4 space-y-3",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{label}</p>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </div>

      <div>
        <p className="text-2xl font-semibold tracking-tight">{value}</p>
        {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
      </div>

      {trend && trendValue && (
        <div className={cn("flex items-center gap-1 text-xs", trendColor)}>
          <TrendIcon className="h-3 w-3" />
          <span>{trendValue}</span>
        </div>
      )}
    </div>
  );
}
