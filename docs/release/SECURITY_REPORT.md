# Security Report — AarogyaAgent v2 RC1

**Generated:** 2026-07-12  
**Auditor:** Automated static analysis + manual code review

---

## 1. Authentication

| Item | Status | Evidence |
|---|---|---|
| JWT token validation enforced | ✅ PASS | `api/v1/router_auth.py` — all protected routes use `Depends(get_current_user)` |
| JWT secret configured via env | ✅ PASS | `core/config.py` — `SECRET_KEY` from env; fails-fast if default key is used in production |
| Token expiry enforced | ✅ PASS | `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60); validated on every request |
| Password hashing | ✅ PASS | `passlib` with `bcrypt` rounds — no plain-text storage |

---

## 2. Authorization / RBAC

| Item | Status | Evidence |
|---|---|---|
| Physician routes protected | ✅ PASS | `require_physician` dependency on all HITL review endpoints |
| Admin routes protected | ✅ PASS | `require_admin` dependency on admin-scope endpoints |
| Patient (anonymous) scope limited | ✅ PASS | Chat routes accessible without auth; no PHI in responses beyond session-scoped chat |
| Metrics API requires auth | ✅ PASS | Verified by integration test `test_metrics_endpoints_unauthorized` — returns 401 |

---

## 3. Security Headers (Middleware Evidence)

All headers injected by `SecurityHeadersMiddleware` on every response:

| Header | Value | Status |
|---|---|---|
| `X-Frame-Options` | `DENY` | ✅ |
| `X-Content-Type-Options` | `nosniff` | ✅ |
| `X-XSS-Protection` | `0` (modern behavior) | ✅ |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | ✅ |
| `Strict-Transport-Security` | Applied in production env only | ✅ |

---

## 4. CORS Configuration

| Item | Status | Evidence |
|---|---|---|
| Explicit origin whitelist | ✅ PASS | `ALLOWED_ORIGINS` env var; defaults to `["http://localhost:3000"]` |
| No wildcard `*` in production | ✅ PASS | Production env example restricts to `https://app.example.com` |
| Credentials allowed | ✅ PASS | `allow_credentials=True` for JWT cookie support |

---

## 5. Rate Limiting

| Item | Status | Evidence |
|---|---|---|
| Rate limiting active | ✅ PASS | `RateLimiterMiddleware` — sliding window per IP |
| Limit configurable | ✅ PASS | `RATE_LIMIT_DEFAULT` env var (default: 100 req/min) |
| 429 response with headers | ✅ PASS | Returns `X-RateLimit-Limit`, `X-RateLimit-Remaining` |
| ⚠️ In-memory only | ⚠️ RISK | Not shared across replicas — Redis required for HA deployment |

---

## 6. Logging Audit

**Static grep of all `logger.info/warning/error/debug` calls against sensitive keywords:** `password`, `token`, `secret`, `bearer`, `authorization`, `api_key`, `phi`, `patient_message`

**Result: No matches found.** ✅

Key observations from `api/middleware.py`:
- `unhandled_exception_handler` logs method + path only, never body
- `aarogya_exception_handler` logs error_code and message, never raw request payload
- `RequestTimingMiddleware` logs duration_ms and status_code only

---

## 7. Input Validation & Request Limits

| Item | Status | Evidence |
|---|---|---|
| Max request size enforced | ✅ PASS | `RequestSizeLimiterMiddleware` — configurable via `MAX_REQUEST_SIZE` (default 5MB) |
| Pydantic schema validation | ✅ PASS | All request bodies are validated via Pydantic schemas; invalid input → 422 |
| No raw SQL constructed from user input | ✅ PASS | All queries use SQLAlchemy ORM — parameterized by default |

---

## 8. Secret Handling

| Item | Status | Evidence |
|---|---|---|
| Secrets loaded from env | ✅ PASS | `pydantic-settings` reads from `.env` / environment variables |
| Production secret enforcement | ✅ PASS | `Settings.adjust_defaults_by_env()` — raises `ValueError` if default `SECRET_KEY` is used in production |
| Secrets not committed | ✅ PASS | `.gitignore` excludes `.env`, `.env.production`; only `.env.example` files are tracked |
| AI API Key from env | ✅ PASS | `OPENAI_API_KEY` via `AIWorkflowSettings`; defaults to `mock-key-for-tests` only |

---

## 9. OWASP Top 10 Assessment

| OWASP Item | Risk | Status |
|---|---|---|
| A01 Broken Access Control | LOW | RBAC enforced via dependencies; 401/403 tested |
| A02 Cryptographic Failures | LOW | bcrypt + JWT HS256; SECRET_KEY enforced in production |
| A03 Injection | LOW | ORM parameterized queries; Pydantic input validation |
| A04 Insecure Design | LOW | CMAR architecture intentionally separates AI and data |
| A05 Security Misconfiguration | MEDIUM | CORS wildcard possible if env not set; docs disabled in production |
| A06 Vulnerable Components | MEDIUM | PostCSS vulnerability in Next.js dependency (accepted, non-exploitable in this context) |
| A07 Auth Failures | LOW | Token expiry, RBAC, bcrypt hashing all in place |
| A08 Integrity Failures | LOW | Docker images from official bases; pip/npm lockfiles present |
| A09 Logging Failures | LOW | Structured logging verified; no PII/secrets in logs |
| A10 SSRF | LOW | No user-controlled URL fetch paths; AI calls go to OpenAI only |

---

## 10. Known Accepted Risks

| Risk | Severity | Acceptance Reason |
|---|---|---|
| PostCSS XSS in Next.js canary | Moderate | Upstream issue; non-exploitable without hostile CSS control; pending Next.js patch |
| In-memory rate limiter | Moderate | Accepted for single-replica deployments; Redis migration documented |
| SQLite in test environment | Low | Test environment only; production requires PostgreSQL |

---

## 11. Future Recommendations

1. Replace in-memory rate limiter with Redis-backed SlowAPI before multi-replica deployment.
2. Add `Content-Security-Policy` header to SecurityHeadersMiddleware.
3. Implement OpenTelemetry-based security event logging.
4. Schedule quarterly dependency vulnerability review.
