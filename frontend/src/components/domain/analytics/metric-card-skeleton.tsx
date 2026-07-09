"use client";

import { cn } from "@/lib/utils";

export function MetricCardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("rounded-lg border border-border bg-card p-4 space-y-3 animate-pulse", className)}>
      <div className="flex items-center justify-between">
        <div className="h-3 w-20 bg-muted rounded" />
        <div className="h-4 w-4 bg-muted rounded" />
      </div>
      <div>
        <div className="h-7 w-16 bg-muted rounded mt-2" />
        <div className="h-3 w-24 bg-muted rounded mt-2" />
      </div>
    </div>
  );
}
