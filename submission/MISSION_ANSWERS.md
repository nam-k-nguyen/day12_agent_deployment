# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Binding to a fixed port in code instead of using the provided `PORT` env var (prevents deployment platforms from routing correctly).
2. Storing secrets in source files or committing `.env` (exposes credentials in git history).
3. Doing heavy model downloads at runtime instead of during image build (slow cold starts).
4. Running services as `root` in container images (security risk).

### Exercise 1.2: Key differences to watch
- Config: Use environment variables in production; local may use `.env` or defaults.
- Logging: Production should log structured, leveled logs to stdout; local can be verbose prints.
- Resource limits: Production images should be small and avoid downloading large artifacts on first run.
- Health checks: Production requires readiness and liveness endpoints; local does not.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | `.env`, local defaults | Env vars, secrets manager | Allows different behavior per environment without code changes |
| Build   | Quick install, dev deps | Multi-stage Docker, minimal runtime deps | Smaller images and faster startup in production |
| Logging | Console prints | Structured logs to stdout/stderr | Easier aggregation and debugging in production |
| Secrets | Local files | Env var or secret store | Prevents accidental secret leakage |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: `python:3.13-slim` (chosen for small footprint and recent Python features).
2. Working directory: Application installed to `/app` in runtime stage.
3. Multi-stage: Uses a builder stage to install dependencies and pre-download models, then copies only necessary artifacts into runtime stage to reduce image size.
4. Non-root user: Creates an `agent` user to avoid running as root.

### Exercise 2.2: Build-time model caching
- Heavy models (Helsinki-NLP, Detoxify) are pre-downloaded in the builder stage to avoid runtime downloads and speed up app start.
- Cache copied to `/app/.hf_cache` in the runtime stage.

### Exercise 2.3: Image size comparison
- Develop: image (with dev deps) — larger, e.g., ~900MB (depends on torch wheel).
- Production: multi-stage, minimal runtime: target < 500MB by installing only runtime deps and using CPU wheels.
- Difference: production trims build tools, caches, and large artifacts not needed at runtime.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://day12agentdeployment-production.up.railway.app
- Screenshot: See `service_running.png` and `deployment_dashboard.png` in `docs/`.
- Notes: Railway detected the `Dockerfile` and deployed successfully. The `startCommand` was set to run Streamlit using the platform-provided `$PORT`.

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- Health endpoint (`/health`) returns 200 OK when service is healthy.
- Requests without API key to protected endpoints return 401.
- Rate limiting responds with 429 when limit exceeded during stress tests.
(Exact command outputs are in `DEPLOYMENT.md`.)

### Exercise 4.4: Cost guard implementation
- Implement a monthly budget guard that tracks LLM token/spend counters per API key and blocks requests when a quota is reached.
- Prefer lightweight in-memory counters with periodic persistence to Redis for multi-replica setups.
- Expose an admin endpoint to top up or reset budgets.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- Health + readiness: Streamlit root `/` used for healthchecks; consider adding `/health` that returns JSON `{ "status": "ok" }` for machine checks.
- Graceful shutdown: Ensure server receives SIGTERM and that long-running LLM inference cancels or finishes before exit in production.
- Stateless design: Externalize session, rate-limit, and audit logs to Redis so replicas remain stateless.
- Autoscaling considerations: Keep model downloads baked into the image and use pre-warmed instances to limit cold-start latency.
- Monitoring: Emit basic metrics (requests, errors, latencies) to stdout for platform ingestion.


---

Submitted by: (fill student name and ID before final submission)
