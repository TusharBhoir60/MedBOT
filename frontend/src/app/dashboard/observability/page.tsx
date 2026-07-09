"use client";

import { useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { PhysicianLayout } from "@/components/layout/physician-layout";
import { AnalyticsRefreshButton } from "@/components/domain/analytics/analytics-refresh-button";
import { useMetricsActivity, metricsKeys } from "@/hooks/use-metrics";
import { ActivityFeed } from "@/schemas/metrics.schema";
import { formatDistanceToNow, parseISO } from "date-fns";
import {
  MessageSquarePlus, ClipboardCheck, ClipboardX, UserCheck, MessageSquare,
  RefreshCw, AlertCircle, ArrowDown, Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const EVENT_ICONS: Record<string, React.ElementType> = {
  conversation_created: MessageSquarePlus,
  conversation_updated: MessageSquare,
  review_created: ClipboardCheck,
  review_assigned: UserCheck,
  review_approved: ClipboardCheck,
  review_rejected: ClipboardX,
  review_overridden: AlertCircle,
  review_comment_added: MessageSquare,
};

const EVENT_COLORS: Record<string, string> = {
  conversation_created: "text-blue-500",
  conversation_updated: "text-blue-400",
  review_created: "text-amber-500",
  review_assigned: "text-violet-500",
  review_approved: "text-green-500",
  review_rejected: "text-red-500",
  review_overridden: "text-orange-500",
  review_comment_added: "text-sky-500",
};

function ActivityItem({ item }: { item: ActivityFeed["items"][number] }) {
  const Icon = EVENT_ICONS[item.type] ?? Activity;
  const color = EVENT_COLORS[item.type] ?? "text-muted-foreground";
  const parsedDate = parseISO(item.timestamp);

  return (
    <li className="flex gap-4 py-4 group" aria-label={item.description}>
      {/* Timeline connector */}
      <div className="flex flex-col items-center">
        <div className={cn("flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted", color.replace("text-", "bg-").replace("500", "100").replace("400", "100"))}>
          <Icon className={cn("h-4 w-4", color)} aria-hidden="true" />
        </div>
        <div className="mt-1 flex-1 w-px bg-border" />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 pb-4">
        <p className="text-sm text-foreground leading-snug">{item.description}</p>
        <div className="flex items-center gap-2 mt-1 flex-wrap">
          <span className="text-xs text-muted-foreground" title={parsedDate.toISOString()}>
            {formatDistanceToNow(parsedDate, { addSuffix: true })}
          </span>
          <span className="text-xs text-muted-foreground/50">·</span>
          <span className="text-xs font-mono text-muted-foreground/70">
            {parsedDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </span>
        </div>
      </div>
    </li>
  );
}

function ActivityEmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
        <Activity className="h-6 w-6 text-muted-foreground" />
      </div>
      <h3 className="text-sm font-medium mb-1">No activity yet</h3>
      <p className="text-sm text-muted-foreground max-w-[280px]">
        Activity events will appear here once conversations and reviews are created.
      </p>
    </div>
  );
}

export default function ObservabilityPage() {
  const queryClient = useQueryClient();
  const [cursor, setCursor] = useState<string | undefined>(undefined);
  const [allItems, setAllItems] = useState<ActivityFeed["items"]>([]);
  const [hasInitiallyLoaded, setHasInitiallyLoaded] = useState(false);

  const { data, isLoading, isError, error, refetch, isRefetching } = useMetricsActivity(
    { limit: 20, cursor },
  );

  // Accumulate items as user paginates
  if (data && !hasInitiallyLoaded) {
    setAllItems(data.items);
    setHasInitiallyLoaded(true);
  }

  const handleLoadMore = useCallback(() => {
    if (!data?.nextCursor) return;
    setAllItems((prev) => [...prev, ...(data?.items ?? [])]);
    setCursor(data.nextCursor ?? undefined);
  }, [data]);

  const handleRefresh = useCallback(() => {
    setCursor(undefined);
    setAllItems([]);
    setHasInitiallyLoaded(false);
    queryClient.invalidateQueries({ queryKey: metricsKeys.activity() });
  }, [queryClient]);

  return (
    <PhysicianLayout>
      <div className="p-6 sm:p-10 max-w-[800px] mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/50 mb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Operational Activity</h1>
            <p className="text-sm text-muted-foreground mt-1">Safe operational events from persisted application data</p>
          </div>
          <AnalyticsRefreshButton onRefresh={handleRefresh} isRefetching={isRefetching} />
        </div>

        {/* Telemetry availability disclaimer — mandatory, non-removable */}
        <div className="rounded-xl border border-border bg-muted/30 p-4 mb-6">
          <p className="text-xs text-muted-foreground leading-relaxed">
            <strong>Observability scope:</strong> Request-level telemetry, error-rate history, latency percentiles,
            and distributed traces are not currently collected. Future observability integration is planned
            through <strong>OpenTelemetry</strong> and <strong>Prometheus</strong>.
            This feed shows safe operational events derived from persisted database records only.
          </p>
        </div>

        {/* Activity Feed */}
        {isLoading && !hasInitiallyLoaded && (
          <div className="space-y-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="flex gap-4 py-3 animate-pulse">
                <div className="h-8 w-8 rounded-full bg-muted shrink-0" />
                <div className="flex-1 space-y-2 pt-1">
                  <div className="h-3 w-3/4 bg-muted rounded" />
                  <div className="h-2.5 w-24 bg-muted rounded" />
                </div>
              </div>
            ))}
          </div>
        )}

        {isError && (
          <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-8 text-center">
            <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-3" />
            <p className="text-sm text-destructive font-medium">Failed to load activity</p>
            <p className="text-xs text-muted-foreground mt-1 mb-4">{error?.message ?? "Unknown error"}</p>
            <button onClick={() => refetch()} className="text-xs text-primary underline">Try again</button>
          </div>
        )}

        {!isLoading && !isError && allItems.length === 0 && <ActivityEmptyState />}

        {allItems.length > 0 && (
          <>
            <ul className="divide-y divide-border/0" aria-label="Operational activity feed">
              {allItems.map((item) => (
                <ActivityItem key={item.id} item={item} />
              ))}
            </ul>

            {/* Load More */}
            {data?.nextCursor && (
              <div className="flex justify-center mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLoadMore}
                  disabled={isRefetching}
                  className="gap-2"
                >
                  {isRefetching ? (
                    <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <ArrowDown className="h-3.5 w-3.5" />
                  )}
                  Load More
                </Button>
              </div>
            )}

            {!data?.nextCursor && allItems.length > 0 && (
              <p className="text-center text-xs text-muted-foreground mt-6">
                All activity events loaded ({allItems.length} total)
              </p>
            )}
          </>
        )}
      </div>
    </PhysicianLayout>
  );
}
