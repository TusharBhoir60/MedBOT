# Backend Metrics & Analytics API

## Overview

The Metrics API provides analytical endpoints for AarogyaAgent v2, conforming strictly to the requirement of using real persisted application data. All endpoints are read-only and perform aggregations using the underlying PostgreSQL/SQLite database.

## Authentication & Authorization

All `/api/v1/metrics/*` endpoints require authentication via a valid JWT bearer token.
The user must have the `physician` or `admin` role. 

- **401 Unauthorized**: If no valid token is provided.
- **403 Forbidden**: If the user is authenticated but lacks required roles.

## Common Query Parameters

All metric endpoints (except `/activity` and `/system`) accept optional date filtering parameters:

- `start_date` (string, ISO-8601, optional): Inclusive lower bound (`start_date <= timestamp`)
- `end_date` (string, ISO-8601, optional): Exclusive upper bound (`timestamp < end_date`)

All dates are normalized to UTC for evaluation.

## Endpoints

### 1. Overview Metrics

`GET /api/v1/metrics/overview`

Provides top-level system aggregates.

**Response (camelCase)**:
- `totalConversations` (int): Count of all `ChatSession` instances.
- `totalReviewTasks` (int): Count of all `ReviewTask` instances.
- `pendingReviews` (int): Count of `NEW` tasks.
- `assignedReviews` (int): Count of `ASSIGNED` tasks.
- `underReview` (int): Count of `UNDER_REVIEW` tasks.
- `approvedReviews` (int): Count of `APPROVED` tasks.
- `rejectedReviews` (int): Count of `REJECTED` tasks.
- `overriddenReviews` (int): Count of `OVERRIDDEN` tasks.
- `closedReviews` (int): Count of `CLOSED` tasks.
- `averageConfidence` (float | null): Average of `combined` score across all sessions.
- `averageReviewTimeSeconds` (float | null): Average duration (`updated_at - created_at`) for resolved tasks.
- `escalationRate` (float | null): Ratio of distinct conversations with a review task to total conversations.
- `averageMessagesPerConversation` (float | null): Average length of the `messages` array in `ChatSession.state`.
- `generatedAt` (string, ISO-8601): Timestamp of generation.

**Null Semantics**: Averages and rates without valid denominators return `null`. Empty counts return `0`.

---

### 2. Confidence Analytics

`GET /api/v1/metrics/confidence`

Provides insights into the CMAR confidence scores.

**Response (camelCase)**:
- `averageConfidence` (float | null): Overall average combined confidence.
- `minimumConfidence` (float | null): Lowest combined confidence.
- `maximumConfidence` (float | null): Highest combined confidence.
- `sampleSize` (int): Number of valid combined confidence scores evaluated.
- `distribution` (array): Breakdown of confidence in fixed buckets: `[0.0, 0.2), [0.2, 0.4), [0.4, 0.6), [0.6, 0.8), [0.8, 1.0]`.
- `agentAverages` (array): Average confidence by individual agent (e.g. intake, symptom, diagnosis).
- `conditionAverages` (array): Average confidence grouped by primary condition (top 20).
- `lowConfidenceCases` (int): Count of cases where confidence falls below the configured threshold.
- `lowConfidenceThreshold` (float): The threshold used to determine low confidence cases (from settings).
- `generatedAt` (string, ISO-8601): Timestamp of generation.

---

### 3. Review Workflow Analytics

`GET /api/v1/metrics/reviews`

Provides insights into the human-in-the-loop review workflow.

**Response (camelCase)**:
- `total` (int): Total review tasks.
- `new` / `assigned` / `underReview` / `approved` / `rejected` / `overridden` / `closed` (int): Counts by status.
- `approvalRate` (float | null): `approved` / resolved total.
- `rejectionRate` (float | null): `rejected` / resolved total.
- `overrideRate` (float | null): `overridden` / resolved total.
- `averageResolutionTimeSeconds` (float | null): Average duration for resolved tasks.
- `throughput` (array): Count of resolved tasks grouped by date.
- `generatedAt` (string, ISO-8601): Timestamp of generation.

**Denominator Note**: The denominator for rates includes only tasks with statuses `APPROVED`, `REJECTED`, `OVERRIDDEN`, and `CLOSED`.

---

### 4. Clinical Distribution Metrics

`GET /api/v1/metrics/clinical`

Analyzes structured medical outputs.

**Response (camelCase)**:
- `topSymptoms` (array): Top 50 reported symptoms, normalized and grouped.
- `topConditions` (array): Top 50 conditions diagnosed by the system.
- `severityDistribution` (array): Counts of urgency levels.
- `escalationDistribution` (array): Tasks grouped by review status as a proxy for escalation distribution.
- `sampleSize` (int): Total number of review tasks analyzed.
- `generatedAt` (string, ISO-8601): Timestamp of generation.

---

### 5. Activity Feed

`GET /api/v1/metrics/activity`

Safe operational activity feed.

**Query Parameters**:
- `limit` (int, default: 20, max: 100)
- `cursor` (string, optional)

**Response (camelCase)**:
- `items` (array): List of event items containing `id`, `type`, `description`, and `timestamp`.
- `nextCursor` (string | null): Opaque cursor for pagination.
- `generatedAt` (string, ISO-8601): Timestamp of generation.

---

### 6. System Health Metrics

`GET /api/v1/metrics/system`

Provides operational health status.

**Response (camelCase)**:
- `overallStatus` (string): 'healthy' or 'degraded'.
- `components` (array): List of components (e.g., database, vector_store) with their status and latency.
- `generatedAt` (string, ISO-8601): Timestamp of generation.

## Known Limitations and Future Instrumentation

The following requested historical telemetry data is **unsupported** because the system does not currently persist request-level metrics:
- Historical request counts
- Error counts
- Latency percentiles
- Retry totals
- Historical health checks
- Rate-limit event counts

**Recommendation for Sprint 8B/9**: Integrate Prometheus (via prometheus-client) and OpenTelemetry to export and visualize these operational metrics properly.
