"use client";

import { BarChart3 } from "lucide-react";

interface ChartEmptyStateProps {
  title?: string;
  description?: string;
}

export function ChartEmptyState({
  title = "No data available",
  description = "There is not enough data to display this chart for the selected period.",
}: ChartEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[250px] w-full text-center border-2 border-dashed border-border rounded-lg p-6 bg-muted/20">
      <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center mb-3 text-muted-foreground">
        <BarChart3 className="h-5 w-5" />
      </div>
      <h4 className="text-sm font-medium">{title}</h4>
      <p className="text-sm text-muted-foreground mt-1 max-w-[250px] mx-auto">{description}</p>
    </div>
  );
}
