import { z } from "zod";

export const MetricsOverviewSchema = z.object({
  totalConversations: z.number().int(),
  totalReviewTasks: z.number().int(),
  pendingReviews: z.number().int(),
  assignedReviews: z.number().int(),
  underReview: z.number().int(),
  approvedReviews: z.number().int(),
  rejectedReviews: z.number().int(),
  overriddenReviews: z.number().int(),
  closedReviews: z.number().int(),
  averageConfidence: z.number().nullable(),
  averageReviewTimeSeconds: z.number().nullable(),
  escalationRate: z.number().nullable(),
  averageMessagesPerConversation: z.number().nullable(),
  generatedAt: z.string().datetime(),
});

export type MetricsOverview = z.infer<typeof MetricsOverviewSchema>;

export const ConfidenceDistributionBucketSchema = z.object({
  minimum: z.number(),
  maximum: z.number(),
  count: z.number().int(),
});

export const AgentConfidenceSchema = z.object({
  agent: z.string(),
  average: z.number(),
  sampleSize: z.number().int(),
});

export const ConditionConfidenceSchema = z.object({
  condition: z.string(),
  average: z.number(),
  sampleSize: z.number().int(),
});

export const ConfidenceMetricsSchema = z.object({
  averageConfidence: z.number().nullable(),
  minimumConfidence: z.number().nullable(),
  maximumConfidence: z.number().nullable(),
  sampleSize: z.number().int(),
  distribution: z.array(ConfidenceDistributionBucketSchema),
  agentAverages: z.array(AgentConfidenceSchema),
  conditionAverages: z.array(ConditionConfidenceSchema),
  lowConfidenceCases: z.number().int(),
  lowConfidenceThreshold: z.number(),
  generatedAt: z.string().datetime(),
});

export type ConfidenceMetrics = z.infer<typeof ConfidenceMetricsSchema>;

export const ReviewThroughputSchema = z.object({
  date: z.string(),
  count: z.number().int(),
});

export const ReviewMetricsSchema = z.object({
  total: z.number().int(),
  new: z.number().int(),
  assigned: z.number().int(),
  underReview: z.number().int(),
  approved: z.number().int(),
  rejected: z.number().int(),
  overridden: z.number().int(),
  closed: z.number().int(),
  approvalRate: z.number().nullable(),
  rejectionRate: z.number().nullable(),
  overrideRate: z.number().nullable(),
  averageResolutionTimeSeconds: z.number().nullable(),
  throughput: z.array(ReviewThroughputSchema),
  generatedAt: z.string().datetime(),
});

export type ReviewMetrics = z.infer<typeof ReviewMetricsSchema>;

export const SymptomCountSchema = z.object({
  name: z.string(),
  count: z.number().int(),
});

export const ConditionCountSchema = z.object({
  name: z.string(),
  count: z.number().int(),
});

export const SeverityCountSchema = z.object({
  name: z.string(),
  count: z.number().int(),
});

export const EscalationDistributionSchema = z.object({
  name: z.string(),
  count: z.number().int(),
});

export const ClinicalMetricsSchema = z.object({
  topSymptoms: z.array(SymptomCountSchema),
  topConditions: z.array(ConditionCountSchema),
  severityDistribution: z.array(SeverityCountSchema),
  escalationDistribution: z.array(EscalationDistributionSchema),
  sampleSize: z.number().int(),
  generatedAt: z.string().datetime(),
});

export type ClinicalMetrics = z.infer<typeof ClinicalMetricsSchema>;

export const ActivityItemSchema = z.object({
  id: z.string(),
  type: z.string(),
  description: z.string(),
  timestamp: z.string().datetime(),
});

export const ActivityFeedSchema = z.object({
  items: z.array(ActivityItemSchema),
  nextCursor: z.string().nullable(),
  generatedAt: z.string().datetime(),
});

export type ActivityFeed = z.infer<typeof ActivityFeedSchema>;

export const SystemComponentHealthSchema = z.object({
  name: z.string(),
  status: z.enum(["healthy", "degraded", "unhealthy"]),
  latencyMs: z.number().nullable(),
  message: z.string().nullable().optional(),
});

export const SystemMetricsSchema = z.object({
  overallStatus: z.enum(["healthy", "degraded", "unhealthy"]),
  components: z.array(SystemComponentHealthSchema),
  generatedAt: z.string().datetime(),
});

export type SystemMetrics = z.infer<typeof SystemMetricsSchema>;
