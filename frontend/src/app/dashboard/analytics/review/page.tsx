"use client";

import { useQueryClient } from "@tanstack/react-query";
import { PhysicianLayout } from "@/components/layout/physician-layout";
import { AnalyticsFilterBar } from "@/components/domain/analytics/analytics-filter-bar";
import { AnalyticsRefreshButton } from "@/components/domain/analytics/analytics-refresh-button";
import { AnalyticsMetricCard } from "@/components/domain/analytics/metric-card";
import { MetricCardSkeleton } from "@/components/domain/analytics/metric-card-skeleton";
import { ChartCard } from "@/components/domain/analytics/chart-card";
import { ChartEmptyState } from "@/components/domain/analytics/chart-empty-state";
import { ChartErrorState } from "@/components/domain/analytics/chart-error-state";
import { useReviewMetrics, metricsKeys } from "@/hooks/use-metrics";
import { MetricsFilters } from "@/services/metrics.service";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from "recharts";
import {
  ClipboardList, CheckCircle2, XCircle, AlertTriangle, Clock, Info,
} from "lucide-react";

function useMetricsFilters(): MetricsFilters {
  if (typeof window === "undefined") return {};
  const sp = new URLSearchParams(window.location.search);
  return {
    startDate: sp.get("startDate") ?? undefined,
    endDate: sp.get("endDate") ?? undefined,
  };
}

function ResolutionTimeDisclaimer() {
  return (
    <div className="rounded-xl border border-amber-200 dark:border-amber-900 bg-amber-50 dark:bg-amber-950/40 p-4 mb-6 flex gap-3">
      <Info className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />
      <p className="text-sm text-amber-800 dark:text-amber-300">
        <strong>Resolution time note:</strong> Average resolution time is currently calculated using{" "}
        <code className="font-mono text-xs bg-amber-100 dark:bg-amber-900 px-1 rounded">ReviewTask.updatedAt</code> as a proxy,
        because the backend does not yet persist a dedicated <code className="font-mono text-xs bg-amber-100 dark:bg-amber-900 px-1 rounded">resolvedAt</code> timestamp.
        This approximation assumes no further edits occur after a task reaches a terminal status.
      </p>
    </div>
  );
}

function ReviewMetricSummary({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, isError, error, refetch } = useReviewMetrics(filters);

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => <MetricCardSkeleton key={i} />)}
      </div>
    );
  }
  if (isError) {
    return (
      <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-6 text-center text-sm text-destructive">
        {error?.message ?? "Failed to load review metrics."}
        <button onClick={() => refetch()} className="ml-2 underline">Retry</button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
      <AnalyticsMetricCard label="Total Reviews" value={data?.total ?? null} format="number" icon={ClipboardList} />
      <AnalyticsMetricCard label="Approved" value={data?.approved ?? null} format="number" icon={CheckCircle2} />
      <AnalyticsMetricCard label="Rejected" value={data?.rejected ?? null} format="number" icon={XCircle} />
      <AnalyticsMetricCard label="Overridden" value={data?.overridden ?? null} format="number" icon={AlertTriangle} />
      <AnalyticsMetricCard label="Approval Rate" value={data?.approvalRate ?? null} format="percent" icon={CheckCircle2} />
      <AnalyticsMetricCard label="Rejection Rate" value={data?.rejectionRate ?? null} format="percent" icon={XCircle} />
      <AnalyticsMetricCard label="Override Rate" value={data?.overrideRate ?? null} format="percent" icon={AlertTriangle} />
      <AnalyticsMetricCard label="Avg Resolution Time" value={data?.averageResolutionTimeSeconds ?? null} format="duration" icon={Clock} description="Via updatedAt proxy" />
    </div>
  );
}

function ReviewOutcomeChart({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, isError, error, refetch } = useReviewMetrics(filters);
  if (isLoading) return <div className="h-[300px] w-full animate-pulse rounded bg-muted/40" />;
  if (isError) return <ChartErrorState error={error} onRetry={refetch} />;

  const resolved = (data?.approved ?? 0) + (data?.rejected ?? 0) + (data?.overridden ?? 0) + (data?.closed ?? 0);
  if (!data || resolved === 0) return <ChartEmptyState description="No resolved review data for this period." />;

  const chartData = [
    { name: "Approved", value: data.approved, color: "hsl(120, 61%, 50%)" },
    { name: "Rejected", value: data.rejected, color: "hsl(0, 84%, 60%)" },
    { name: "Overridden", value: data.overridden, color: "hsl(280, 65%, 60%)" },
    { name: "Closed", value: data.closed, color: "hsl(220, 13%, 60%)" },
  ].filter((d) => d.value > 0);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const formatTooltip = (val: any) => [typeof val === 'number' ? val.toLocaleString() : val, "Reviews"];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart aria-label="Review outcome distribution donut chart">
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={70}
          outerRadius={110}
          paddingAngle={2}
          dataKey="value"
          nameKey="name"
        >
          {chartData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
        </Pie>
        <Tooltip formatter={formatTooltip} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

function ThroughputChart({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, isError, error, refetch } = useReviewMetrics(filters);
  if (isLoading) return <div className="h-[300px] w-full animate-pulse rounded bg-muted/40" />;
  if (isError) return <ChartErrorState error={error} onRetry={refetch} />;
  if (!data || !data.throughput || data.throughput.length === 0) return <ChartEmptyState description="No throughput data for this period." />;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data.throughput} aria-label="Review throughput over time chart">
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
        <Tooltip />
        <Bar dataKey="count" name="Resolved" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default function ReviewAnalyticsPage() {
  const queryClient = useQueryClient();
  const filters = useMetricsFilters();
  const { isRefetching } = useReviewMetrics(filters);

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: metricsKeys.reviews(filters) });
  };

  return (
    <PhysicianLayout>
      <div className="p-6 sm:p-10 max-w-[1600px] mx-auto">
        <AnalyticsFilterBar
          title="Review Analytics"
          description="Human-in-the-Loop review workflow performance"
          actions={<AnalyticsRefreshButton onRefresh={handleRefresh} isRefetching={isRefetching} />}
        />

        <ResolutionTimeDisclaimer />

        <section aria-label="Review metrics summary" className="mb-8">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">Summary</h2>
          <ReviewMetricSummary filters={filters} />
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartCard title="Review Outcome Distribution" description="Breakdown of resolved reviews by decision">
            <ReviewOutcomeChart filters={filters} />
          </ChartCard>
          <ChartCard title="Review Throughput Over Time" description="Number of reviews resolved per day">
            <ThroughputChart filters={filters} />
          </ChartCard>
        </div>
      </div>
    </PhysicianLayout>
  );
}
