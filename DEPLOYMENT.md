# Production Deployment Guide

## Prerequisites
- Docker Engine >= 24.0.0
- Docker Compose >= 2.20.0
- External Identity Provider (Optional, for now JWT is standalone)
- PostgreSQL 16 with pgvector extension (if not using the bundled db container)

## Configuration
1. Copy `.env.production.example` to `.env.production`:
   ```bash
   cp .env.production.example .env.production
   ```
2. Update the environment variables in `.env.production`.
   > [!IMPORTANT]
   > You MUST change the `SECRET_KEY`. Run `openssl rand -hex 32` to generate a secure key.
   > The backend will fail to start if the default development `SECRET_KEY` is used in production.

## Running the Stack
1. Start the services using Docker Compose:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```
2. Verify the containers are healthy:
   ```bash
   docker ps
   ```

## Observability
- Logs are emitted in JSON format via standard out when `LOG_FORMAT=JSON`.
- We recommend configuring the Docker daemon to forward logs to a central aggregator (e.g., Datadog, ELK, Splunk) using the docker logging drivers.
- Every API request log contains a `correlation_id` to trace requests through the entire system.

## Health Endpoints
- **Liveness**: `GET /api/v1/health/live` - Used for container restart policies.
- **Readiness**: `GET /api/v1/health/ready` - Used by load balancers to route traffic.
- **Diagnostics**: `GET /api/v1/health` - Component-level status (DB, Vector Store, Uptime).

## Database Migrations
Migrations are run inside the container automatically or manually:
```bash
docker exec -it aarogya_api_prod alembic upgrade head
```
