import { describe, it, expect } from "vitest";
import {
  MetricsOverviewSchema,
  ConfidenceMetricsSchema,
  ReviewMetricsSchema,
  ClinicalMetricsSchema,
  ActivityFeedSchema,
  SystemMetricsSchema,
} from "@/schemas/metrics.schema";

// ── Fixtures ──────────────────────────────────────────────────────────────────

const VALID_OVERVIEW = {
  totalConversations: 42,
  totalReviewTasks: 10,
  pendingReviews: 2,
  assignedReviews: 1,
  underReview: 1,
  approvedReviews: 4,
  rejectedReviews: 1,
  overriddenReviews: 0,
  closedReviews: 1,
  averageConfidence: 0.82,
  averageReviewTimeSeconds: 360.5,
  escalationRate: 0.24,
  averageMessagesPerConversation: 4.2,
  generatedAt: "2026-07-09T10:00:00.000Z",
};

const VALID_CONFIDENCE = {
  averageConfidence: 0.75,
  minimumConfidence: 0.1,
  maximumConfidence: 0.99,
  sampleSize: 100,
  distribution: [
    { minimum: 0.0, maximum: 0.2, count: 5 },
    { minimum: 0.2, maximum: 0.4, count: 10 },
    { minimum: 0.4, maximum: 0.6, count: 20 },
    { minimum: 0.6, maximum: 0.8, count: 40 },
    { minimum: 0.8, maximum: 1.0, count: 25 },
  ],
  agentAverages: [{ agent: "intake", average: 0.8, sampleSize: 100 }],
  conditionAverages: [{ condition: "Flu", average: 0.9, sampleSize: 5 }],
  lowConfidenceCases: 15,
  lowConfidenceThreshold: 0.4,
  generatedAt: "2026-07-09T10:00:00.000Z",
};

const VALID_REVIEWS = {
  total: 10,
  new: 2,
  assigned: 1,
  underReview: 1,
  approved: 4,
  rejected: 1,
  overridden: 0,
  closed: 1,
  approvalRate: 0.667,
  rejectionRate: 0.167,
  overrideRate: 0.0,
  averageResolutionTimeSeconds: 720.0,
  throughput: [{ date: "2026-07-08", count: 3 }],
  generatedAt: "2026-07-09T10:00:00.000Z",
};

const VALID_CLINICAL = {
  topSymptoms: [{ name: "Fever", count: 20 }],
  topConditions: [{ name: "Flu", count: 15 }],
  severityDistribution: [{ name: "routine", count: 25 }],
  escalationDistribution: [{ name: "APPROVED", count: 4 }],
  sampleSize: 30,
  generatedAt: "2026-07-09T10:00:00.000Z",
};

const VALID_ACTIVITY = {
  items: [
    {
      id: "abc123",
      type: "review_approved",
      description: "Review task approved",
      timestamp: "2026-07-09T09:30:00.000Z",
    },
  ],
  nextCursor: null,
  generatedAt: "2026-07-09T10:00:00.000Z",
};

const VALID_SYSTEM = {
  overallStatus: "healthy",
  components: [
    { name: "database", status: "healthy", latencyMs: 12.3 },
    { name: "vector_store", status: "degraded", latencyMs: 890.0 },
  ],
  generatedAt: "2026-07-09T10:00:00.000Z",
};

// ── Overview schema tests ─────────────────────────────────────────────────────

describe("MetricsOverviewSchema", () => {
  it("parses a valid response", () => {
    const result = MetricsOverviewSchema.parse(VALID_OVERVIEW);
    expect(result.totalConversations).toBe(42);
    expect(result.averageConfidence).toBe(0.82);
  });

  it("accepts null for all nullable fields", () => {
    const data = {
      ...VALID_OVERVIEW,
      averageConfidence: null,
      averageReviewTimeSeconds: null,
      escalationRate: null,
      averageMessagesPerConversation: null,
    };
    const result = MetricsOverviewSchema.parse(data);
    expect(result.averageConfidence).toBeNull();
    expect(result.escalationRate).toBeNull();
  });

  it("rejects missing required integer fields", () => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { totalConversations: _tc, ...rest } = VALID_OVERVIEW;
    expect(() => MetricsOverviewSchema.parse(rest)).toThrow();
  });
});

// ── Confidence schema tests ───────────────────────────────────────────────────

describe("ConfidenceMetricsSchema", () => {
  it("parses a valid confidence response", () => {
    const result = ConfidenceMetricsSchema.parse(VALID_CONFIDENCE);
    expect(result.lowConfidenceThreshold).toBe(0.4);
    expect(result.distribution).toHaveLength(5);
  });

  it("accepts all-null nullable fields", () => {
    const data = {
      ...VALID_CONFIDENCE,
      averageConfidence: null,
      minimumConfidence: null,
      maximumConfidence: null,
    };
    const result = ConfidenceMetricsSchema.parse(data);
    expect(result.averageConfidence).toBeNull();
  });

  it("accepts empty distribution and agent arrays", () => {
    const data = { ...VALID_CONFIDENCE, distribution: [], agentAverages: [], conditionAverages: [] };
    const result = ConfidenceMetricsSchema.parse(data);
    expect(result.distribution).toHaveLength(0);
  });
});

// ── Review schema tests ───────────────────────────────────────────────────────

describe("ReviewMetricsSchema", () => {
  it("parses a valid review response", () => {
    const result = ReviewMetricsSchema.parse(VALID_REVIEWS);
    expect(result.approvalRate).toBeCloseTo(0.667);
  });

  it("accepts null rates", () => {
    const data = { ...VALID_REVIEWS, approvalRate: null, rejectionRate: null, overrideRate: null };
    const result = ReviewMetricsSchema.parse(data);
    expect(result.approvalRate).toBeNull();
  });

  it("accepts empty throughput array", () => {
    const data = { ...VALID_REVIEWS, throughput: [] };
    const result = ReviewMetricsSchema.parse(data);
    expect(result.throughput).toHaveLength(0);
  });
});

// ── Clinical schema tests ─────────────────────────────────────────────────────

describe("ClinicalMetricsSchema", () => {
  it("parses a valid clinical response", () => {
    const result = ClinicalMetricsSchema.parse(VALID_CLINICAL);
    expect(result.topSymptoms[0].name).toBe("Fever");
  });

  it("accepts all empty arrays", () => {
    const data = {
      ...VALID_CLINICAL,
      topSymptoms: [],
      topConditions: [],
      severityDistribution: [],
      escalationDistribution: [],
    };
    const result = ClinicalMetricsSchema.parse(data);
    expect(result.topSymptoms).toHaveLength(0);
  });
});

// ── Activity schema tests ─────────────────────────────────────────────────────

describe("ActivityFeedSchema", () => {
  it("parses a valid activity response", () => {
    const result = ActivityFeedSchema.parse(VALID_ACTIVITY);
    expect(result.items).toHaveLength(1);
    expect(result.nextCursor).toBeNull();
  });

  it("accepts a nextCursor string", () => {
    const data = { ...VALID_ACTIVITY, nextCursor: "cursor_abc123" };
    const result = ActivityFeedSchema.parse(data);
    expect(result.nextCursor).toBe("cursor_abc123");
  });

  it("accepts empty items array", () => {
    const data = { ...VALID_ACTIVITY, items: [] };
    const result = ActivityFeedSchema.parse(data);
    expect(result.items).toHaveLength(0);
  });

  it("rejects items missing required fields", () => {
    const data = { ...VALID_ACTIVITY, items: [{ id: "x", type: "review_approved" }] };
    expect(() => ActivityFeedSchema.parse(data)).toThrow();
  });
});

// ── System schema tests ───────────────────────────────────────────────────────

describe("SystemMetricsSchema", () => {
  it("parses a valid system response", () => {
    const result = SystemMetricsSchema.parse(VALID_SYSTEM);
    expect(result.overallStatus).toBe("healthy");
    expect(result.components[1].status).toBe("degraded");
  });

  it("rejects unknown status values", () => {
    const data = { ...VALID_SYSTEM, overallStatus: "unknown_status" };
    expect(() => SystemMetricsSchema.parse(data)).toThrow();
  });

  it("rejects component with unknown status", () => {
    const data = {
      ...VALID_SYSTEM,
      components: [{ name: "db", status: "partially_ok", latencyMs: 5 }],
    };
    expect(() => SystemMetricsSchema.parse(data)).toThrow();
  });
});
