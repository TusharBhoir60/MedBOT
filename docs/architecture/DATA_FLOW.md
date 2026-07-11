# Data Flow Architecture

## Overview
This document illustrates the flow of data through AarogyaAgent v2 during a standard patient triage interaction and subsequent physician review.

## Sequence Diagram: Patient Intake to Physician Review

```mermaid
sequenceDiagram
    actor Patient
    participant Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant AI as LangGraph Engine
    participant RAG as ChromaDB
    actor Physician

    %% Patient Interaction
    Patient->>Frontend: Sends chat message ("I have a fever")
    Frontend->>API: POST /api/v1/chat/invoke
    
    %% Backend Processing
    API->>DB: Fetch session state
    DB-->>API: Current State JSON
    
    API->>AI: ainvoke(state, message)
    
    %% AI Engine Execution
    AI->>AI: Intake Agent (extracts demographics)
    AI->>AI: Symptom Agent (extracts "fever")
    
    AI->>RAG: Diagnosis Agent queries vector store
    RAG-->>AI: WHO Dengue Guidelines
    
    AI->>AI: Confidence Aggregator & Check
    
    %% Handoff Decision
    alt Confidence is Low / Emergency Detected
        AI->>DB: Creates ReviewTask (status: pending)
        AI-->>API: Returns Escalation Message
    else Confidence is High
        AI-->>API: Returns Differential Diagnosis
    end
    
    %% State Persistence
    API->>DB: Persist updated state JSON
    API-->>Frontend: HTTP 200 (AI Response)
    Frontend-->>Patient: Displays message
    
    %% Physician Review
    Physician->>Frontend: Opens Dashboard
    Frontend->>API: GET /api/v1/reviews/pending
    API->>DB: Fetch pending tasks
    DB-->>API: Tasks list
    API-->>Frontend: Tasks data
    
    Physician->>Frontend: Approves diagnosis with notes
    Frontend->>API: POST /api/v1/reviews/{id}/approve
    API->>DB: Update ReviewTask (status: approved)
    DB-->>API: Success
    API-->>Frontend: HTTP 200 OK
```

## Data Lifecycle

### 1. Ephemeral State
During the execution of a LangGraph turn, state mutations are kept in memory and managed deterministically by the Graph's Reducers.

### 2. Persistent State
At the conclusion of the graph execution, the entire state dictionary (including chat history, extracted symptoms, and confidence schemas) is serialized to JSON and persisted to the `ChatSession` table in PostgreSQL.

### 3. Asynchronous Tasks
When a physician updates a `ReviewTask`, the backend modifies the task row. The `MetricsService` independently queries these rows to generate aggregated analytics.
