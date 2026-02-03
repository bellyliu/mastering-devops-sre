# OpenTelemetry Quick Start Guide

## What Was Added

This implementation adds distributed tracing to the FastAPI Book Store application using OpenTelemetry and Jaeger.

### Files Created/Modified

**New Files:**
- [OTEL_INTRODUCTION.md](OTEL_INTRODUCTION.md) - Complete OpenTelemetry concepts guide
- [OTEL_IMPLEMENTATION_GUIDE.md](OTEL_IMPLEMENTATION_GUIDE.md) - Step-by-step implementation guide
- [app/tracing.py](app/tracing.py) - OpenTelemetry configuration and setup

**Modified Files:**
- [docker-compose.yaml](docker-compose.yaml) - Added Jaeger service and networking
- [requirements.txt](requirements.txt) - Added OpenTelemetry packages
- [app/main.py](app/main.py) - Integrated OpenTelemetry instrumentation

---

## Quick Start (3 Steps)

### 1. Start All Services

```bash
cd /Users/dekribellyliu/bellyliu/mastering-devops-sre/applications/fast-api/postgresql

# Rebuild with new dependencies
docker-compose build api

# Start everything (including Jaeger)
docker-compose up -d

# Check logs
docker-compose logs -f api
```

You should see:
```
✅ OpenTelemetry configured for service: bookstore-api
📊 Sending traces to: http://jaeger:4318/v1/traces
```

### 2. Generate Some Traffic

```bash
# Health check
curl http://localhost:8000/health

# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "Alice123!"
  }'

# Login (save the token)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=Alice123!" | jq -r '.access_token')

echo "Token: $TOKEN"

# Create a book
curl -X POST http://localhost:8000/books/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Distributed Tracing with OpenTelemetry",
    "author": "Jane Doe",
    "description": "Learn how to implement observability",
    "year": 2025,
    "isbn": "978-1234567890"
  }'

# Get all books
curl http://localhost:8000/books/

# Get specific book
curl http://localhost:8000/books/1
```

### 3. View Traces in Jaeger UI

1. **Open Jaeger UI**: http://localhost:16686
2. **Select Service**: `bookstore-api`
3. **Select Operation**: 
   - `POST /auth/register`
   - `POST /auth/login`
   - `POST /books/`
   - `GET /books/`
4. **Click "Find Traces"**

---

## What You'll See in Jaeger

### Example Trace: Create Book

```
POST /books/ (Total: 245ms)
├─ authenticate_user (85ms)
│  └─ SELECT FROM users (PostgreSQL) (40ms)
├─ validate_book_data (5ms)
├─ INSERT INTO books (PostgreSQL) (120ms)
└─ cache_invalidation (Redis) (25ms)
```

### Key Insights

- **Total Request Time**: 245ms
- **Database Time**: 160ms (65% of total)
- **Auth Overhead**: 85ms (35%)
- **Bottleneck**: Database INSERT operation

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  User → FastAPI (Port 8000)                     │
│         ├─ Automatic OTEL Instrumentation       │
│         ├─ Traces HTTP requests                 │
│         ├─ Traces DB queries (PostgreSQL)       │
│         └─ Traces Redis operations              │
└─────────────────────────────────────────────────┘
                     ↓ OTLP Export
┌─────────────────────────────────────────────────┐
│  Jaeger (Port 16686)                            │
│  ├─ Collector receives traces                   │
│  ├─ Stores in memory (dev mode)                 │
│  └─ UI for visualization                        │
└─────────────────────────────────────────────────┘
```

---

## What Gets Traced Automatically

✅ **All HTTP Requests**
- Method, path, status code
- Request/response headers
- Duration

✅ **Database Queries**
- SQL statements
- Query duration
- Connection info

✅ **Redis Operations**
- Commands (GET, SET, etc.)
- Key names
- Duration

✅ **Authentication**
- JWT creation
- Password verification
- User lookups

---

## Environment Variables (Optional)

Create `.env` file for customization:

```bash
# OpenTelemetry Settings
OTEL_ENABLED=true
OTEL_SERVICE_NAME=bookstore-api
OTEL_EXPORTER_ENDPOINT=http://jaeger:4318/v1/traces
OTEL_SAMPLING_RATE=1.0  # 100% for dev, 0.1 for production
```

---

## Jaeger UI Features

### 1. Search Traces
- Filter by time range
- Filter by duration (e.g., > 100ms)
- Filter by tags
- Find error traces

### 2. Trace Details
- Waterfall view of spans
- Span duration
- Attributes (tags)
- Events and errors

### 3. Service Graph
- Visualize dependencies
- See service interactions
- Identify bottlenecks

### 4. Compare Traces
- Compare fast vs slow requests
- Identify performance anomalies
- Find regression patterns

---

## Troubleshooting

### No traces appearing?

```bash
# 1. Check Jaeger is running
docker-compose ps jaeger

# 2. Check API can reach Jaeger
docker-compose exec api ping jaeger

# 3. Check logs for errors
docker-compose logs api | grep -i otel
docker-compose logs jaeger

# 4. Verify OTLP endpoint
docker-compose exec api curl http://jaeger:4318/v1/traces
```

### Application running slow?

Automatic instrumentation adds ~2-5% latency. For production:

1. Reduce sampling to 10%:
   ```python
   # In app/tracing.py
   sampler = TraceIdRatioBased(0.1)
   ```

2. Exclude health checks:
   ```python
   FastAPIInstrumentor.instrument_app(
       app,
       excluded_urls="/health,/metrics"
   )
   ```

---

## Next Steps

### 1. Add Custom Spans

For specific business logic, add manual spans:

```python
from app.tracing import get_tracer
from opentelemetry.trace import Status, StatusCode

tracer = get_tracer(__name__)

def process_payment(amount: float):
    with tracer.start_as_current_span("process_payment") as span:
        span.set_attribute("amount", amount)
        span.set_attribute("currency", "USD")
        
        # Your logic here
        
        span.set_status(Status(StatusCode.OK))
```

### 2. Production Setup

- Use persistent storage (Cassandra or Elasticsearch)
- Set sampling to 5-10%
- Add resource attributes (region, version)
- Set up alerts for errors and slow traces

### 3. Explore Metrics

OpenTelemetry also supports metrics:

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)
request_counter = meter.create_counter("http_requests_total")
request_counter.add(1, {"method": "POST", "endpoint": "/books/"})
```

---

## Documentation

- **Concepts**: See [OTEL_INTRODUCTION.md](OTEL_INTRODUCTION.md)
- **Detailed Implementation**: See [OTEL_IMPLEMENTATION_GUIDE.md](OTEL_IMPLEMENTATION_GUIDE.md)
- **Official Docs**: https://opentelemetry.io/docs/languages/python/

---

## Services Overview

| Service | Port | Description |
|---------|------|-------------|
| **FastAPI** | 8000 | Book Store API with OTEL |
| **PostgreSQL** | 5432 | Database |
| **Redis** | 6379 | Cache |
| **Jaeger UI** | 16686 | Trace visualization |
| **OTLP Collector** | 4318 | Trace ingestion |

---

## Quick Commands

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop everything
docker-compose down

# Restart just API
docker-compose restart api

# View Jaeger logs
docker-compose logs jaeger

# Access Jaeger UI
open http://localhost:16686
```

---

**You're all set!** Generate some API traffic and explore traces in Jaeger UI at http://localhost:16686 🚀
