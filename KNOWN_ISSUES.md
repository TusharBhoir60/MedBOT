# Known Issues

The following known limitations exist in the v1.0.0 release of AarogyaAgent v2.

### 1. Analytics & Observability
- **Tooltips on Recharts**: Strict TypeScript typings for `Recharts` tooltip formatters conflict with Next.js 16/React 19 types, forcing the use of an explicit `any` bypass or ESLint disable directives.
- **Latency Disclaimers**: Historic component latency is not preserved. Only point-in-time latency is calculated when the System Health dashboard is loaded. True time-series telemetry requires a Prometheus/Grafana stack to be integrated (scheduled for post-v1.0.0).

### 2. Dependency Issues
- **PostCSS Vulnerability**: `next@16.3.0-canary.5` relies on a minor version of `postcss` that flags an XSS vulnerability (`GHSA-qx2v-qp2m-jg93`). Resolving this currently forces an aggressive downgrade of the framework itself. The XSS vulnerability requires hostile CSS stringify output control, which is currently non-exploitable in the isolated frontend. Kept intact per the Dependency Update Policy (no breaking major-version modifications).

### 3. Performance
- **LangGraph Chat Pipeline Latency**: Due to complex RAG retrievals and LLM reasoning cycles, Chat API requests can occasionally drift towards 8 seconds during cold starts or deep vector searches.
