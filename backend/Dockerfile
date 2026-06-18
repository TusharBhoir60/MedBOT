# syntax=docker/dockerfile:1.6
# ─────────────────────────────────────────────
# Stage 1: builder — install dependencies into an isolated venv
# ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build tools needed for asyncpg (C extension)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtualenv to isolate dependencies from the system Python
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ─────────────────────────────────────────────
# Stage 2: runtime — slim image, copy venv only
# ─────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Runtime libpq only (no build tools in final image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy venv from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY . .

# Set ownership so the non-root user can read all files
RUN chown -R appuser:appgroup /app

USER appuser

# Health check using the liveness endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/live')" || exit 1

EXPOSE 8000

# Run with uvicorn; workers=1 for container-native scaling (scale replicas, not processes)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log"]
