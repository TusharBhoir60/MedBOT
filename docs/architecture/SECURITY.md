# Security Architecture

## Overview
AarogyaAgent v2 adheres to strict security constraints due to its nature as a healthcare technology application.

## Authentication & Authorization
- **JWT (JSON Web Tokens):** Stateless authentication mechanism. Tokens are signed using HS256.
- **RBAC (Role-Based Access Control):** Defined roles (`patient`, `physician`, `admin`). Endpoints use FastAPI `Depends(require_role("physician"))` to enforce authorization at the router level.
- **Password Hashing:** `passlib` with `bcrypt` is used to hash all user passwords. Raw passwords are never logged or stored.

## Data Protection
- **Data in Transit:** All traffic is expected to be TLS/HTTPS terminated at the load balancer or ingress controller.
- **SQL Injection Prevention:** Pure SQLAlchemy 2.0 ORM usage inherently escapes inputs. No raw SQL concatenation exists in the repository.
- **Cross-Site Scripting (XSS):** React's default DOM escaping protects the frontend against standard XSS injection through chat messages.

## OWASP Considerations
- **Rate Limiting:** (Future Roadmap) Endpoints should be protected by an ingress rate limiter to prevent DoS via excessive AI invocations.
- **Dependency Scanning:** The CI pipeline routinely updates and audits dependencies. A known vulnerability in `postcss` exists upstream in Next.js but does not impact the runtime client environment.

## AI Security
- **Prompt Injection:** Hardcoded safety validators intercept malformed or malicious inputs designed to manipulate the LLM.
- **PHI Masking:** (Future Roadmap) Personally Identifiable Information should be scrubbed before hitting the OpenAI API. Currently, users are advised not to input real names.
