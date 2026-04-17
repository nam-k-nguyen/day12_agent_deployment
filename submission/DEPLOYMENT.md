# Deployment Information

## Public URL
https://day12agentdeployment-production.up.railway.app

## Platform
Railway

## Service Details
- Builder: Dockerfile (multi-stage)
- Start command used on platform: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- Region: us-west2 (as shown in Railway dashboard screenshot)

## Environment Variables Set (expected)
- PORT (injected by Railway)
- OPENAI_API_KEY (set via Railway variables)
- ENVIRONMENT (optional)
- Any other keys required by `defense` pipeline (e.g., external router keys)

## Test Commands

### Health Check
```bash
curl -i https://day12agentdeployment-production.up.railway.app/health
# Expected: 200 and a small JSON or HTML response indicating the app is serving
```

### UI Availability (Streamlit root)
```bash
curl -I https://day12agentdeployment-production.up.railway.app/
# Expected: HTTP/2 200 or 301/302 depending on headers; returns Streamlit HTML
```

### API Test (example protected endpoint)
```bash
curl -X POST https://day12agentdeployment-production.up.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"Hello"}'
# Expected: 200 with assistant response (401 if missing/invalid API key)
```

### Rate limiting test (example)
```bash
for i in {1..15}; do \
  curl -s -o /dev/null -w "%{http_code}\n" -X POST https://day12agentdeployment-production.up.railway.app/ask \
    -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" \
    -d '{"user_id":"test","question":"test"}'; \
done
# Expected: Mostly 200 until the configured limit, then 429 responses when exceeded
```

## Health and Logs Notes
- The Railway dashboard shows `Deployment successful` in the attached dashboard screenshot.
- Common issues to check in Railway logs:
  - Missing environment variables (causes runtime crash)
  - Binding to a non-injected port (must use `$PORT`)
  - Build-time failures (dependency errors)

## Images / Screenshots
- Deployment dashboard: ![Deployment Dashboard](deployment_dashboard.png)
- Service running (Streamlit UI): ![Service Running](service_running.png)


## Environment Template
Create `.env.example` locally with keys you must set in Railway:

```
# Example .env.example
OPENAI_API_KEY=
ENVIRONMENT=production
# Any other keys required by your pipeline
```

---
