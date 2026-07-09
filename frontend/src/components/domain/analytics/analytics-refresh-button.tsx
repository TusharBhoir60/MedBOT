"use client";

import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

interface AnalyticsRefreshButtonProps {
  onRefresh: () => void;
  isRefetching?: boolean;
}

export function AnalyticsRefreshButton({ onRefresh, isRefetching }: AnalyticsRefreshButtonProps) {
  return (
    <Button
      variant="outline"
      size="icon"
      onClick={onRefresh}
      disabled={isRefetching}
      className="h-8 w-8 shrink-0"
      title="Refresh data"
    >
      <RefreshCw className={cn("h-4 w-4", isRefetching && "animate-spin text-primary")} />
      <span className="sr-only">Refresh</span>
    </Button>
  );
}
