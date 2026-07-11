# Deployment Architecture

## Overview
The application is fully containerized using Docker, enabling deployment across any modern container orchestration platform (e.g., Kubernetes, AWS ECS, Google Cloud Run).

## Container Strategy
### Backend
- Base Image: `python:3.12-slim`
- Optimizations: Uses a non-root user, prevents `.pyc` file generation, and limits memory bloat.

### Frontend
- Base Image: `node:20-alpine`
- Optimizations: Utilizes Next.js `output: "standalone"` to create a minimal production build, drastically reducing the final image size and attack surface by excluding unnecessary `node_modules`.

## CI/CD Pipeline
GitHub Actions manages the CI/CD lifecycle across four distinct workflows:
1. `backend.yml`: Runs Pytest, checks formatting (Ruff), and evaluates coverage.
2. `frontend.yml`: Runs Jest, linting, and Next.js build verification.
3. `e2e.yml`: Executes the Playwright End-to-End browser test suite against a fully orchestrated docker-compose environment.
4. `release.yml`: Automates version tagging and asset generation upon merges to the main branch.

## Environment Configuration
Production environments require the injection of specific environment variables (see `.env.example`).
Critical variables include:
- `DATABASE_URL` (Must point to a robust PostgreSQL cluster, e.g., AWS RDS)
- `OPENAI_API_KEY`
- `JWT_SECRET_KEY`

## Observability
The application exposes standardized health probes:
- `/api/v1/health/live`: Liveness probe for Kubernetes restarts.
- `/api/v1/health/ready`: Readiness probe verifying downstream database and AI connections before accepting traffic.
