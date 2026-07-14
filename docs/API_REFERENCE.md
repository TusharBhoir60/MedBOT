# AarogyaAgent API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Protected endpoints require a JWT token passed in the `Authorization` header:
```http
Authorization: Bearer <your_jwt_token>
```

---

## 1. Authentication

### `POST /auth/login`
Authenticates a user and returns a JWT token.

**Request Body:**
```json
{
  "username": "dr_smith",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5c...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "dr_smith",
    "role": "physician"
  }
}
```

---

## 2. Chat (Patient Workflow)

### `POST /chat/invoke`
Sends a message to the AI engine and returns the updated state.

**Request Body:**
```json
{
  "session_id": "session-123",
  "message": "I've had a high fever since yesterday.",
  "patient_info": {
    "age": 45,
    "gender": "male"
  },
  "symptoms": ["fever"]
}
```

**Response (200 OK):**
```json
{
  "session_id": "session-123",
  "turn_count": 1,
  "messages": [
    {"role": "human", "content": "I've had a high fever since yesterday."},
    {"role": "ai", "content": "I understand. Do you have any other symptoms like a rash or joint pain?"}
  ],
  "extracted_symptoms": {"fever": {"severity": "high", "duration": "1 day"}},
  "confidence_scores": {
    "combined": {
      "score": 0.85,
      "source": "confidence_aggregator",
      "uncertainty_factors": ["missing specific temperature"],
      "reasoning": "Weighted: intake=0.90 + symptom=0.80",
      "requires_followup": true,
      "requires_human": false
    }
  }
}
```

---

## 3. Review Workflow (Physician Workflow)
*Requires `physician` role.*

### `GET /reviews/pending`
Fetches a list of review tasks awaiting physician intervention.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "session_id": "session-123",
    "patient_info": {"age": 45},
    "symptoms": ["chest pain"],
    "status": "pending",
    "created_at": "2026-07-12T00:00:00Z"
  }
]
```

### `POST /reviews/{task_id}/approve`
Approves a pending task, optionally appending physician notes.

**Request Body:**
```json
{
  "notes": "Patient requires immediate ECG."
}
```

---

## 4. Metrics & Analytics
*Requires `physician` role.*

All metric endpoints (except `/activity` and `/system`) accept optional date filtering parameters:
- `start_date` (string, ISO-8601, optional): Inclusive lower bound
- `end_date` (string, ISO-8601, optional): Exclusive upper bound

### `GET /metrics/overview`
Retrieves aggregated system usage and clinical metrics.

**Response (camelCase):**
- `totalConversations` (int): Count of all ChatSession instances.
- `totalReviewTasks` (int): Count of all ReviewTask instances.
- `pendingReviews` / `assignedReviews` / `underReview` / `approvedReviews` / `rejectedReviews` / `overriddenReviews` / `closedReviews` (int): Counts by status.
- `averageConfidence` (float | null): Average of combined score across all sessions.
- `averageReviewTimeSeconds` (float | null): Average duration for resolved tasks.
- `escalationRate` (float | null): Ratio of distinct conversations with a review task to total conversations.
- `averageMessagesPerConversation` (float | null): Average length of the messages array.
- `generatedAt` (string, ISO-8601): Timestamp of generation.

### `GET /metrics/confidence`
Provides insights into the CMAR confidence scores.

**Response (camelCase):**
- `averageConfidence` (float | null): Overall average combined confidence.
- `minimumConfidence` / `maximumConfidence` (float | null).
- `sampleSize` (int): Number of valid combined confidence scores evaluated.
- `distribution` (array): Breakdown of confidence in fixed buckets.
- `agentAverages` (array): Average confidence by individual agent.
- `conditionAverages` (array): Average confidence grouped by primary condition.
- `lowConfidenceCases` (int): Count of cases where confidence falls below the configured threshold.
- `lowConfidenceThreshold` (float).
- `generatedAt` (string, ISO-8601).

### `GET /metrics/reviews`
Provides insights into the human-in-the-loop review workflow.

**Response (camelCase):**
- `total` (int): Total review tasks.
- `approvalRate` / `rejectionRate` / `overrideRate` (float | null).
- `averageResolutionTimeSeconds` (float | null).
- `throughput` (array): Count of resolved tasks grouped by date.
- `generatedAt` (string, ISO-8601).

### `GET /metrics/clinical`
Analyzes structured medical outputs.

**Response (camelCase):**
- `topSymptoms` (array): Top 50 reported symptoms.
- `topConditions` (array): Top 50 conditions diagnosed by the system.
- `severityDistribution` (array): Counts of urgency levels.
- `escalationDistribution` (array): Tasks grouped by review status.
- `sampleSize` (int): Total number of review tasks analyzed.
- `generatedAt` (string, ISO-8601).

### `GET /metrics/activity`
Safe operational activity feed.

**Query Parameters:**
- `limit` (int, default: 20, max: 100)
- `cursor` (string, optional)

**Response (camelCase):**
- `items` (array): List of event items containing `id`, `type`, `description`, and `timestamp`.
- `nextCursor` (string | null): Opaque cursor for pagination.
- `generatedAt` (string, ISO-8601).

---

## 5. Health Probes

### `GET /health/live`
Standard Kubernetes liveness probe.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptimeSeconds": 3600
}
```

### `GET /health/ready`
Standard Kubernetes readiness probe checking DB and LLM connectivity.

**Response (200 OK / 503 Unavailable):**
```json
{
  "status": "healthy",
  "database": "connected",
  "vectorStore": "connected",
  "llmProvider": "healthy",
  "dbLatencyMs": 45.2
}
```

### `GET /metrics/system`
Provides operational health status.

**Response (camelCase):**
- `overallStatus` (string): 'healthy' or 'degraded'.
- `components` (array): List of components (e.g., database, vector_store) with their status and latency.
- `generatedAt` (string, ISO-8601).

---

## Error Handling
Standard error schema for all 4xx/5xx responses:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed",
    "details": {"field": "message cannot be empty"},
    "timestamp": "2026-07-12T00:00:00Z",
    "correlationId": "req-123abc456"
  }
}
```
