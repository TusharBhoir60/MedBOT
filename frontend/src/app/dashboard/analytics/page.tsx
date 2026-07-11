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
import { useMetricsOverview, useReviewMetrics, useClinicalMetrics, metricsKeys } from "@/hooks/use-metrics";
import { MetricsFilters } from "@/services/metrics.service";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from "recharts";
import {
  MessageSquare, ClipboardList, Clock, CheckCircle2, XCircle, AlertTriangle,
  TrendingUp, Users, Brain, Layers,
} from "lucide-react";

// Semantic color palette — using CSS vars to stay theme-compatible
const STATUS_COLORS: Record<string, string> = {
  new: "hsl(var(--chart-1, 220 91% 60%))",
  assigned: "hsl(var(--chart-2, 160 84% 39%))",
  under_review: "hsl(var(--chart-3, 47 92% 55%))",
  approved: "hsl(var(--chart-4, 120 61% 50%))",
  rejected: "hsl(var(--chart-5, 0 84% 60%))",
  overridden: "hsl(var(--chart-6, 280 65% 60%))",
  closed: "hsl(var(--chart-1, 220 13% 60%))",
};

// Helper: extract date filters from URL search params
function useMetricsFilters(): MetricsFilters {
  if (typeof window === "undefined") return {};
  const sp = new URLSearchParams(window.location.search);
  return {
    startDate: sp.get("startDate") ?? undefined,
    endDate: sp.get("endDate") ?? undefined,
  };
}

function OverviewSection({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, isError, error, refetch } = useMetricsOverview(filters);

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
        Failed to load overview metrics: {error?.message ?? "Unknown error"}
        <button onClick={() => refetch()} className="ml-2 underline">Retry</button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
      <AnalyticsMetricCard label="Total Conversations" value={data?.totalConversations ?? null} format="number" icon={MessageSquare} />
      <AnalyticsMetricCard label="Total Review Tasks" value={data?.totalReviewTasks ?? null} format="number" icon={ClipboardList} />
      <AnalyticsMetricCard label="Pending Reviews" value={data?.pendingReviews ?? null} format="number" icon={Clock} />
      <AnalyticsMetricCard label="Under Review" value={data?.underReview ?? null} format="number" icon={Users} />
      <AnalyticsMetricCard label="Approved" value={data?.approvedReviews ?? null} format="number" icon={CheckCircle2} />
      <AnalyticsMetricCard label="Rejected" value={data?.rejectedReviews ?? null} format="number" icon={XCircle} />
      <AnalyticsMetricCard label="Overridden" value={data?.overriddenReviews ?? null} format="number" icon={AlertTriangle} />
      <AnalyticsMetricCard label="Average Confidence" value={data?.averageConfidence ?? null} format="percent" icon={Brain} description="Combined CMAR score" />
      <AnalyticsMetricCard label="Escalation Rate" value={data?.escalationRate ?? null} format="percent" icon={TrendingUp} description="Conversations with review task" />
      <AnalyticsMetricCard label="Avg Review Time" value={data?.averageReviewTimeSeconds ?? null} format="duration" icon={Clock} description="Based on updatedAt proxy" />
      <AnalyticsMetricCard label="Avg Messages" value={data?.averageMessagesPerConversation ?? null} format="number" icon={Layers} description="Per conversation" />
    </div>
  );
}

function ReviewStatusChart({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, isError, error, refetch } = useReviewMetrics(filters);

  if (isLoading) return <div className="h-[300px] w-full animate-pulse rounded bg-muted/40" />;
  if (isError) return <ChartErrorState error={error} onRetry={refetch} />;
  if (!data || data.total === 0) return <ChartEmptyState />;

  const chartData = [
    { name: "New", value: data.new, color: STATUS_COLORS.new },
    { name: "Assigned", value: data.assigned, color: STATUS_COLORS.assigned },
    { name: "Under Review", value: data.underReview, color: STATUS_COLORS.under_review },
    { name: "Approved", value: data.approved, color: STATUS_COLORS.approved },
    { name: "Rejected", value: data.rejected, color: STATUS_COLORS.rejected },
    { name: "Overridden", value: data.overridden, color: STATUS_COLORS.overridden },
    { name: "Closed", value: data.closed, color: STATUS_COLORS.closed },
  ].filter((d) => d.value > 0);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const formatTooltip = (val: any) => [typeof val === 'number' ? val.toLocaleString() : val, "Tasks"];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart aria-label="Review status distribution chart">
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={70}
          outerRadius={110}
          paddingAngle={2}
          dataKey="value"
          nameKey="name"
          label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ""}: ${((percent ?? 0) * 100).toFixed(0)}%`}
          labelLine={false}
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
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
  if (!data || !data.throughput || data.throughput.length === 0) return <ChartEmptyState description="No review throughput data for this period." />;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data.throughput} aria-label="Daily review throughput chart">
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
        <Tooltip />
        <Bar dataKey="count" name="Reviews" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function TopSymptomsChart({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, isError, error, refetch } = useClinicalMetrics(filters);

  if (isLoading) return <div className="h-[300px] w-full animate-pulse rounded bg-muted/40" />;
  if (isError) return <ChartErrorState error={error} onRetry={refetch} />;
  if (!data || data.topSymptoms.length === 0) return <ChartEmptyState description="No symptom data for this period." />;

  const top10 = data.topSymptoms.slice(0, 10);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={top10} layout="vertical" aria-label="Top reported symptoms chart">
        <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
        <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={120} />
        <Tooltip />
        <Bar dataKey="count" name="Cases" fill="hsl(var(--chart-2, 160 84% 39%))" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function SeverityChart({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, isError, error, refetch } = useClinicalMetrics(filters);

  if (isLoading) return <div className="h-[300px] w-full animate-pulse rounded bg-muted/40" />;
  if (isError) return <ChartErrorState error={error} onRetry={refetch} />;
  if (!data || data.severityDistribution.length === 0) return <ChartEmptyState description="No severity data for this period." />;

  const SEVERITY_COLORS = ["hsl(var(--chart-4,120 61% 50%))", "hsl(var(--chart-3,47 92% 55%))", "hsl(var(--chart-5,0 84% 60%))"];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart aria-label="Severity distribution chart">
        <Pie
          data={data.severityDistribution}
          cx="50%"
          cy="50%"
          outerRadius={110}
          dataKey="count"
          nameKey="name"
          label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ""}: ${((percent ?? 0) * 100).toFixed(0)}%`}
        >
          {data.severityDistribution.map((_, i) => (
            <Cell key={i} fill={SEVERITY_COLORS[i % SEVERITY_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

export default function AnalyticsPage() {
  const queryClient = useQueryClient();
  const filters = useMetricsFilters();
  const { isRefetching: overviewRefetching } = useMetricsOverview(filters);

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: metricsKeys.all });
  };

  return (
    <PhysicianLayout>
      <div className="p-6 sm:p-10 max-w-[1600px] mx-auto">
        <AnalyticsFilterBar
          title="Analytics"
          description="Real-time aggregations from persisted application data"
          actions={<AnalyticsRefreshButton onRefresh={handleRefresh} isRefetching={overviewRefetching} />}
        />

        {/* Overview metrics grid */}
        <section aria-label="Overview metrics" className="mb-8">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">Overview</h2>
          <OverviewSection filters={filters} />
        </section>

        {/* Charts grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartCard title="Review Status Distribution" description="Breakdown of all review tasks by current status">
            <ReviewStatusChart filters={filters} />
          </ChartCard>

          <ChartCard title="Daily Review Throughput" description="Number of reviews resolved per day">
            <ThroughputChart filters={filters} />
          </ChartCard>

          <ChartCard title="Top Reported Symptoms" description="Most frequently reported symptoms across all cases">
            <TopSymptomsChart filters={filters} />
          </ChartCard>

          <ChartCard title="Case Severity Distribution" description="Distribution of urgency levels across triage outcomes">
            <SeverityChart filters={filters} />
          </ChartCard>
        </div>
      </div>
    </PhysicianLayout>
  );
}
