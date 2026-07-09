"use client";

import { ReactNode } from "react";
import { DateRangeFilter } from "./date-range-filter";

interface AnalyticsFilterBarProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  showDateFilter?: boolean;
}

export function AnalyticsFilterBar({ title, description, actions, showDateFilter = true }: AnalyticsFilterBarProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/50 mb-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        {description && <p className="text-sm text-muted-foreground mt-1">{description}</p>}
      </div>
      <div className="flex items-center gap-4">
        {showDateFilter && <DateRangeFilter />}
        {actions}
      </div>
    </div>
  );
}
