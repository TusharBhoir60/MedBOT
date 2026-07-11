# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-07-11

### Added
- **AI Agent System (CMAR)**: Complex Multi-Agent Reasoning workflow via LangGraph for robust, accurate patient conversations.
- **Frontend App**: Next.js App Router providing AI Chat, Analytics Dashboards, and Human-in-the-Loop review queues.
- **Metrics API**: Fully featured observability and usage API for analytics consumption.
- **Human-in-the-Loop (HITL)**: Workflow for physicians to approve, reject, or override AI outputs.
- **Persistent Sessions**: SQLAlchemy/PostgreSQL backed chat sessions, ensuring historical continuity.
- **Playwright E2E**: End-to-end testing coverage across the system.

### Changed
- Standardized UI using Tailwind CSS v4 and shadcn/ui.
- Refactored backend dependencies into strict Repository and Service layers.
- Expanded backend and frontend CI/CD configurations into modular GitHub Actions.

### Security
- Integrated robust JWT Authentication with Role-Based Access Control (RBAC).
- Completed extensive OWASP and API Security Top 10 audits prior to release.
