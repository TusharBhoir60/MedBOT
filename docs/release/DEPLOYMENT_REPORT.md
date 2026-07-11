# Deployment Report — AarogyaAgent v2 RC1

**Generated:** 2026-07-12

---

## 1. Docker Architecture

### Backend Container (Multi-stage Build)

**File:** `backend/Dockerfile`  
**Stages:**

| Stage | Base Image | Purpose |
|---|---|---|
| `builder` | `python:3.12-slim` | Installs pip deps into isolated `/opt/venv` |
| `runtime` | `python:3.12-slim` | Copies venv only; runs the application |

**Security features verified in Dockerfile:**
- ✅ Non-root user: `adduser --system --ingroup appgroup appuser`
- ✅ `chown -R appuser:appgroup /app` for correct file permissions
- ✅ `USER appuser` set before CMD
- ✅ Only `libpq5` runtime lib (no build tools in final image)
- ✅ `HEALTHCHECK` configured at container level
- ✅ No secrets baked into image layers

### Frontend Container (Multi-stage Build)

**File:** `frontend/Dockerfile`  
**Defect Found and Fixed During RC1 Audit:** The original Dockerfile was a single-stage development image (`npm run dev`). This was **corrected** to a proper 3-stage production build:

| Stage | Base Image | Purpose |
|---|---|---|
| `deps` | `node:20-alpine` | Installs production-only `node_modules` |
| `builder` | `node:20-alpine` | Runs `npm run build` (Next.js compilation) |
| `runner` | `node:20-alpine` | Copies only `standalone` output; runs `node server.js` |

**Security features in corrected Dockerfile:**
- ✅ Non-root user: `nextjs` (uid 1001)
- ✅ `NODE_ENV=production` set explicitly
- ✅ Next.js `output: "standalone"` enabled in `next.config.ts`
- ✅ Only static assets and compiled JS included in final image

---

## 2. Docker Compose (Development)

**File:** `docker-compose.yml`

| Service | Image | Health Check | Notes |
|---|---|---|---|
| `db` | `pgvector/pgvector:pg16` | `pg_isready` every 10s | Named volume `postgres_data` |
| `api` | Built from `./backend` | HTTP liveness check every 30s | `depends_on: db: condition: service_healthy` |
| `frontend` | Built from `./frontend` | None | Depends on `api` service |

**Issues noted:**
- ⚠️ Dev compose mounts `./frontend:/app` and `./backend:/app` (hot-reload volumes); these should be absent in production compose.
- ⚠️ DB credentials hardcoded in dev compose (`postgres/postgres`) — acceptable for development; production uses env-file.

---

## 3. Docker Compose (Production)

**File:** `docker-compose.prod.yml`

| Item | Status | Notes |
|---|---|---|
| DB password from env | ✅ | `${DB_PASSWORD}` — no default |
| API uses env-file | ✅ | `env_file: .env.production` |
| Health check on API | ✅ | HTTP liveness probe |
| No volume mounts of source code | ✅ | Production uses pre-built image |
| Frontend service absent | ⚠️ NOTED | `docker-compose.prod.yml` only defines `db` + `api`; frontend deployment assumed via separate CDN/Vercel or full docker-compose extension |

---

## 4. Database Migration Status

**Tool:** Alembic  
**Single head verified:** ✅ `b30679180ef9 (head)`

Migration chain (clean linear history):

```
17a2eec748f8  → Add review models          (base)
18a3ffd849e9  → Add ChatSession model       (parent: 17a2eec748f8)
b30679180ef9  → Add title and is_archived   (parent: 18a3ffd849e9)
```

- ✅ Single head — no branch conflicts
- ✅ No orphan revisions
- ✅ Each migration has both `upgrade()` and `downgrade()` defined

---

## 5. Environment Configuration Consistency

| Variable | `.env.example` | `.env.production.example` | docker-compose.yml | docker-compose.prod.yml |
|---|---|---|---|---|
| `APP_ENV` | ✅ | ✅ | ✅ | Via env-file |
| `DATABASE_URL` | ✅ | ✅ | ✅ | Via env-file |
| `SYNC_DATABASE_URL` | ✅ | ✅ | ✅ | Via env-file |
| `SECRET_KEY` | ❌ Missing | ✅ | ❌ Missing | Via env-file |
| `ALLOWED_HOSTS` | ✅ | ✅ | ✅ | Via env-file |
| `ALLOWED_ORIGINS` | ✅ | ✅ | ✅ | Via env-file |
| `LOG_LEVEL` | ✅ | ✅ | ✅ | Via env-file |
| `OPENAI_API_KEY` | ❌ Missing | ❌ Missing | ❌ Missing | Via env-file |

> [!WARNING]
> `SECRET_KEY` and `OPENAI_API_KEY` are absent from `.env.example` and `.env.production.example`. These must be documented and required. Added to recommendations below.

---

## 6. Defect Corrected During Audit

| # | Defect | Severity | Fix Applied |
|---|---|---|---|
| 1 | Frontend Dockerfile was a dev image (`npm run dev`) | **CRITICAL** | Replaced with 3-stage production build |
| 2 | `next.config.ts` lacked `output: "standalone"` | **HIGH** | Added `output: "standalone"` |
| 3 | `SECRET_KEY` absent from `.env.example` | **MEDIUM** | Documented (env var addition recommended) |

---

## 7. Recommendations

1. Add `SECRET_KEY` and `OPENAI_API_KEY` to `.env.example` (with placeholder values and warnings).
2. Add a frontend service definition to `docker-compose.prod.yml` using the production runner image.
3. Configure a production frontend health check (e.g., curl to `http://localhost:3000/api/health`).
4. Consider adding `STOPSIGNAL SIGTERM` explicitly in both Dockerfiles for graceful shutdown clarity.
