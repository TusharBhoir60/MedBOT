# Frontend Architecture

## Overview
The frontend is a server-side rendered application utilizing Next.js 16 (App Router). It provides two distinct domains: the Patient Chat Interface and the Physician Dashboard.

## Key Technologies
- **Framework:** Next.js 16
- **Language:** TypeScript
- **State Management:** `@tanstack/react-query` v5
- **UI Framework:** Tailwind CSS v4, shadcn/ui
- **Forms & Validation:** `react-hook-form`, `zod`
- **Charts:** `recharts`

## Directory Structure
```text
frontend/src/
├── app/                  # Route definitions (Next.js App Router)
│   ├── (patient)/        # Public-facing patient routes
│   └── dashboard/        # Protected physician routes
├── components/           # Reusable React components
│   ├── ui/               # shadcn/ui primitives
│   ├── chat/             # Chat interface components
│   └── dashboard/        # Analytics and review components
├── lib/                  # Utilities (API client, token management)
└── hooks/                # Custom TanStack Query hooks
```

## Data Fetching Strategy
We rely exclusively on TanStack Query (React Query) for server-state synchronization. 
- **Queries:** Cached, automatically refetched on window focus, used for analytics and task queues.
- **Mutations:** Used for sending chat messages and submitting task reviews.
- **Invalidation:** Mutation successes automatically invalidate relevant queries to ensure real-time UI consistency.

## Authentication Flow
The frontend extracts the JWT token from the backend login response, stores it in an HTTP-Only equivalent/secure context, and injects it into all outgoing API requests using an Axios interceptor (`lib/apiClient.ts`). Protected routes (`/dashboard`) redirect to `/login` if the token is missing or expired.
