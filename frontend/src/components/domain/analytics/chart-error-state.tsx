"use client";

import { AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChartErrorStateProps {
  error?: Error | null;
  onRetry?: () => void;
}

export function ChartErrorState({ error, onRetry }: ChartErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[250px] w-full text-center border-2 border-destructive/20 rounded-lg p-6 bg-destructive/5">
      <div className="h-10 w-10 rounded-full bg-destructive/10 flex items-center justify-center mb-3 text-destructive">
        <AlertCircle className="h-5 w-5" />
      </div>
      <h4 className="text-sm font-medium text-destructive">Failed to load data</h4>
      <p className="text-xs text-muted-foreground mt-1 max-w-[250px] mx-auto mb-4">
        {error?.message || "An unexpected error occurred while fetching chart data."}
      </p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  );
}
