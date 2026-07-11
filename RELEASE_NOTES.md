# Release Notes

## AarogyaAgent v2 (Version 1.0.0)

AarogyaAgent v2 has officially reached Production Readiness. This release marks the culmination of Sprint 9, finalizing the architectural maturity of the platform.

### Highlights
- **End-to-End Test Suite**: Complete UI test coverage for patient interactions and physician review workflows using Playwright.
- **Scalable Architecture**: Docker multi-stage builds are ready for Kubernetes deployment, coupled with modular GitHub Actions pipelines.
- **Reliable AI Inference**: LangGraph implementations have been benchmarked for latency and stability. The system enforces robust P95 latency bounds across Health, Metrics, and Auth endpoints.
- **Zero Mock Analytics**: The analytics dashboard is now 100% driven by realtime PostgreSQL telemetry from the AI usage.

### Important Upgrade Notices
- Database migrations must be run sequentially. Ensure `alembic upgrade head` is executed before starting the API server on a fresh deployment.
- Playwright tests now rely on specific seeded test users (`dr_smith`, `admin`). Make sure these exist in your staging environments if you run the E2E suite remotely.
