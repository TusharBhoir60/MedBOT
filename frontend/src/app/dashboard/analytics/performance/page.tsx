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
import { useConfidenceMetrics, metricsKeys } from "@/hooks/use-metrics";
import { MetricsFilters } from "@/services/metrics.service";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { Brain, AlertTriangle, TrendingDown, TrendingUp, Hash, Info } from "lucide-react";

function useMetricsFilters(): MetricsFilters {
  if (typeof window === "undefined") return {};
  const sp = new URLSearchParams(window.location.search);
  return {
    startDate: sp.get("startDate") ?? undefined,
    endDate: sp.get("endDate") ?? undefined,
  };
}

function ConfidenceExplainer({ threshold }: { threshold: number }) {
  return (
    <div className="rounded-xl border border-primary/20 bg-primary/5 p-5 mb-6">
      <div className="flex gap-3">
        <Info className="h-5 w-5 text-primary shrink-0 mt-0.5" aria-hidden="true" />
        <div>
          <h2 className="text-sm font-semibold mb-1">What is CMAR Confidence?</h2>
          <p className="text-sm text-muted-foreground leading-relaxed">
            AarogyaAgent uses <strong>Confidence-Weighted Multi-Agent Reasoning (CMAR)</strong> to produce a combined
            confidence score between 0 and 1. This score reflects the internal consistency across multiple AI agents
            (intake, symptom analysis, and diagnosis). A higher score means greater agreement between agents.
          </p>
          <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
            <strong>This is not diagnostic certainty.</strong> Confidence measures model agreement, not clinical accuracy.
            Cases falling below the configured threshold of{" "}
            <span className="font-mono font-medium text-foreground">{(threshold * 100).toFixed(0)}%</span>{" "}
            are automatically flagged for physician review.
          </p>
        </div>
      </div>
    </div>
  );
}

function DistributionChart({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, isError, error, refetch } = useConfidenceMetrics(filters);

  if (isLoading) return <div className="h-[300px] w-full animate-pulse rounded bg-muted/40" />;
  if (isError) return <ChartErrorState error={error} onRetry={refetch} />;
  if (!data || data.distribution.length === 0) return <ChartEmptyState description="No confidence distribution data for this period." />;

  const chartData = data.distribution.map(d => ({
    range: `[${d.minimum.toFixed(1)}, ${d.maximum.toFixed(1)}${d.maximum === 1.0 ? ']' : ')'}`,
    count: d.count,
  }));

  const formatTooltip = (val: number | string) => [typeof val === 'number' ? `${val.toLocaleString()}` : val, "Cases"];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} aria-label="Confidence score distribution histogram">
        <XAxis dataKey="range" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
        <Tooltip formatter={formatTooltip} />
        <Bar dataKey="count" name="Cases" radius={[4, 4, 0, 0]}>
          {data.distribution.map((entry, i) => {
            // Color buckets: lower = more red, higher = more green
            const ratio = i / Math.max(data.distribution.length - 1, 1);
            const hue = Math.round(ratio * 120); // 0 = red, 120 = green
            return <Cell key={i} fill={`hsl(${hue}, 65%, 50%)`} />;
          })}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function AgentConfidenceChart({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, isError, error, refetch } = useConfidenceMetrics(filters);

  if (isLoading) return <div className="h-[300px] w-full animate-pulse rounded bg-muted/40" />;
  if (isError) return <ChartErrorState error={error} onRetry={refetch} />;
  if (!data || data.agentAverages.length === 0) return <ChartEmptyState description="No agent confidence data for this period." />;

  const chartData = data.agentAverages.map((a) => ({
    agent: a.agent.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
    average: parseFloat((a.average * 100).toFixed(1)),
  }));

  const formatTooltip = (val: number | string) => [typeof val === 'number' ? `${val}%` : val, "Avg Confidence"];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} aria-label="Per-agent average confidence scores">
        <XAxis dataKey="agent" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
        <Tooltip formatter={formatTooltip} />
        <Bar dataKey="average" name="Confidence" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function ConditionConfidenceChart({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, isError, error, refetch } = useConfidenceMetrics(filters);

  if (isLoading) return <div className="h-[300px] w-full animate-pulse rounded bg-muted/40" />;
  if (isError) return <ChartErrorState error={error} onRetry={refetch} />;
  if (!data || data.conditionAverages.length === 0) return <ChartEmptyState description="No condition-level confidence data for this period." />;

  const top15 = data.conditionAverages.slice(0, 15).map((c) => ({
    condition: c.condition,
    average: parseFloat((c.average * 100).toFixed(1)),
    count: c.sampleSize,
  }));

  const formatTooltip = (val: number | string) => [typeof val === 'number' ? `${val}%` : val, "Avg Confidence"];

  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={top15} layout="vertical" aria-label="Average confidence per condition">
        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
        <YAxis type="category" dataKey="condition" tick={{ fontSize: 11 }} width={140} />
        <Tooltip formatter={formatTooltip} />
        <Bar dataKey="average" name="Confidence" fill="hsl(var(--chart-2, 160 84% 39%))" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default function AIPerformancePage() {
  const queryClient = useQueryClient();
  const filters = useMetricsFilters();
  const { data, isLoading, isRefetching } = useConfidenceMetrics(filters);

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: metricsKeys.confidence(filters) });
  };

  return (
    <PhysicianLayout>
      <div className="p-6 sm:p-10 max-w-[1600px] mx-auto">
        <AnalyticsFilterBar
          title="AI Performance"
          description="CMAR confidence scores and model agreement analysis"
          actions={<AnalyticsRefreshButton onRefresh={handleRefresh} isRefetching={isRefetching} />}
        />

        {data && <ConfidenceExplainer threshold={data.lowConfidenceThreshold} />}

        {/* Metric Cards */}
        <section aria-label="Confidence summary metrics" className="mb-8">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">Summary</h2>
          {isLoading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
              {Array.from({ length: 5 }).map((_, i) => <MetricCardSkeleton key={i} />)}
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
              <AnalyticsMetricCard label="Average Confidence" value={data?.averageConfidence ?? null} format="percent" icon={Brain} />
              <AnalyticsMetricCard label="Min Confidence" value={data?.minimumConfidence ?? null} format="percent" icon={TrendingDown} />
              <AnalyticsMetricCard label="Max Confidence" value={data?.maximumConfidence ?? null} format="percent" icon={TrendingUp} />
              <AnalyticsMetricCard label="Sample Size" value={data?.sampleSize ?? null} format="number" icon={Hash} description="Valid confidence readings" />
              <AnalyticsMetricCard
                label="Low-Confidence Cases"
                value={data?.lowConfidenceCases ?? null}
                format="number"
                icon={AlertTriangle}
                description={data ? `Threshold: ${(data.lowConfidenceThreshold * 100).toFixed(0)}%` : undefined}
              />
            </div>
          )}
        </section>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartCard title="Confidence Distribution" description="How confidence scores are distributed across all cases">
            <DistributionChart filters={filters} />
          </ChartCard>

          <ChartCard title="Agent Average Confidence" description="Average confidence score per reasoning agent">
            <AgentConfidenceChart filters={filters} />
          </ChartCard>

          <div className="lg:col-span-2">
            <ChartCard title="Confidence by Condition" description="Average confidence broken down by primary diagnosis (top 15)">
              <ConditionConfidenceChart filters={filters} />
            </ChartCard>
          </div>
        </div>
      </div>
    </PhysicianLayout>
  );
}
