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

### `GET /metrics/overview`
Retrieves aggregated system usage and clinical metrics.

**Response (200 OK):**
```json
{
  "totalSessions": 150,
  "activeSessions": 12,
  "tasksPending": 5,
  "averageConfidence": 0.89
}
```

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
