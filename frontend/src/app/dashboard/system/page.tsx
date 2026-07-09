"use client";
import React from "react";

import { useQueryClient } from "@tanstack/react-query";
import { PhysicianLayout } from "@/components/layout/physician-layout";
import { AnalyticsRefreshButton } from "@/components/domain/analytics/analytics-refresh-button";
import { useSystemMetrics, metricsKeys } from "@/hooks/use-metrics";
import { formatDistanceToNow } from "date-fns";
import {
  CheckCircle2, AlertTriangle, XCircle, Database, Server, Cpu, ListChecks, RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/utils";

type HealthStatus = "healthy" | "degraded" | "unhealthy";

const STATUS_CONFIG: Record<HealthStatus, { label: string; icon: React.ElementType; className: string; border: string }> = {
  healthy: {
    label: "Healthy",
    icon: CheckCircle2,
    className: "text-green-600 dark:text-green-400",
    border: "border-green-200 dark:border-green-900",
  },
  degraded: {
    label: "Degraded",
    icon: AlertTriangle,
    className: "text-amber-600 dark:text-amber-400",
    border: "border-amber-200 dark:border-amber-900",
  },
  unhealthy: {
    label: "Unhealthy",
    icon: XCircle,
    className: "text-red-600 dark:text-red-400",
    border: "border-red-200 dark:border-red-900",
  },
};

const COMPONENT_ICONS: Record<string, React.ElementType> = {
  database: Database,
  db: Database,
  vector_store: Server,
  vectorstore: Server,
  llm: Cpu,
  llm_provider: Cpu,
  review_queue: ListChecks,
};

function SystemComponentCard({ name, status, latencyMs }: { name: string; status: HealthStatus; latencyMs: number }) {
  const cfg = STATUS_CONFIG[status];
  const Icon = cfg.icon;
  const normalized = name.toLowerCase().replace(/[^a-z_]/g, "");
  const ComponentIconType = COMPONENT_ICONS[normalized] ?? Server;
  const componentIconEl = React.createElement(ComponentIconType, {
    className: "h-5 w-5 text-muted-foreground",
    "aria-hidden": "true",
  });

  return (
    <div
      className={cn("flex items-center gap-4 rounded-xl border bg-card p-5 shadow-sm transition-colors", cfg.border)}
      aria-label={`${name}: ${cfg.label}`}
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
        {componentIconEl}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold capitalize">{name.replace(/_/g, " ")}</p>
        <div className={cn("flex items-center gap-1 mt-0.5 text-xs", cfg.className)}>
          <Icon className="h-3 w-3" aria-hidden="true" />
          <span>{cfg.label}</span>
        </div>
      </div>
      <div className="text-right shrink-0">
        <p className="text-sm font-mono font-medium">{latencyMs.toFixed(0)} ms</p>
        <p className="text-xs text-muted-foreground">latency</p>
      </div>
    </div>
  );
}

function SystemHealthSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 rounded-xl border bg-card p-5 animate-pulse">
          <div className="h-10 w-10 rounded-lg bg-muted" />
          <div className="flex-1 space-y-2">
            <div className="h-3 w-24 bg-muted rounded" />
            <div className="h-2.5 w-16 bg-muted rounded" />
          </div>
          <div className="h-4 w-16 bg-muted rounded" />
        </div>
      ))}
    </div>
  );
}

export default function SystemHealthPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, isError, error, refetch, isRefetching } = useSystemMetrics();

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: metricsKeys.system() });
  };

  const overallCfg = data ? STATUS_CONFIG[data.overallStatus] : null;
  const OverallIcon = overallCfg?.icon ?? RefreshCw;

  return (
    <PhysicianLayout>
      <div className="p-6 sm:p-10 max-w-[1000px] mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/50 mb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">System Health</h1>
            <p className="text-sm text-muted-foreground mt-1">Current operational status of system components</p>
          </div>
          <AnalyticsRefreshButton onRefresh={handleRefresh} isRefetching={isRefetching} />
        </div>

        {/* Overall Status Banner */}
        {!isLoading && !isError && data && (
          <div className={cn(
            "flex items-center gap-3 rounded-xl border p-5 mb-6",
            overallCfg?.border ?? "",
          )}>
            <OverallIcon className={cn("h-6 w-6 shrink-0", overallCfg?.className)} aria-hidden="true" />
            <div>
              <p className="font-semibold">Overall Status: <span className={overallCfg?.className}>{overallCfg?.label}</span></p>
              <p className="text-xs text-muted-foreground mt-0.5">
                Last checked: {formatDistanceToNow(new Date(data.generatedAt), { addSuffix: true })}
              </p>
            </div>
          </div>
        )}

        {/* Component Grid */}
        {isLoading && <SystemHealthSkeleton />}

        {isError && (
          <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-8 text-center">
            <XCircle className="h-8 w-8 text-destructive mx-auto mb-3" />
            <p className="text-sm text-destructive font-medium">Failed to load system health</p>
            <p className="text-xs text-muted-foreground mt-1 mb-4">{error?.message ?? "Unknown error"}</p>
            <button
              onClick={() => refetch()}
              className="text-xs text-primary underline"
            >
              Try again
            </button>
          </div>
        )}

        {!isLoading && !isError && data && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {data.components.map((c) => (
              <SystemComponentCard
                key={c.name}
                name={c.name}
                status={c.status}
                latencyMs={c.latencyMs}
              />
            ))}
          </div>
        )}

        {/* Disclaimer — never show fake uptime/history */}
        <div className="mt-8 rounded-lg border border-border bg-muted/30 p-4">
          <p className="text-xs text-muted-foreground leading-relaxed">
            <strong>Current status only.</strong> This page displays the live result of real health checks performed by the backend
            at the time of this request. Historical uptime percentages and latency trends are not available.
            Future sprint: integrate Prometheus and OpenTelemetry for time-series observability.
          </p>
        </div>
      </div>
    </PhysicianLayout>
  );
}
