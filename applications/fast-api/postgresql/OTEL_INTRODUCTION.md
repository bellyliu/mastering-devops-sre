# OpenTelemetry (OTEL) - Complete Introduction

## What is OpenTelemetry?

**OpenTelemetry** is an open-source observability framework that provides a standardized way to collect, process, and export telemetry data (traces, metrics, and logs) from your applications. It's a Cloud Native Computing Foundation (CNCF) project that merged OpenTracing and OpenCensus.

### The Three Pillars of Observability

```
┌─────────────────────────────────────────────────────┐
│           OpenTelemetry Observability               │
├─────────────────────────────────────────────────────┤
│  1. TRACES      │  2. METRICS     │  3. LOGS        │
│  (Requests)     │  (Numbers)      │  (Events)       │
├─────────────────┼─────────────────┼─────────────────┤
│  • Spans        │  • Counters     │  • Structured   │
│  • Context      │  • Gauges       │  • Unstructured │
│  • Propagation  │  • Histograms   │  • Contextual   │
└─────────────────┴─────────────────┴─────────────────┘
```

---

## Why OpenTelemetry?

### Problems It Solves

**Before OpenTelemetry:**
- ❌ Multiple competing standards (OpenTracing, OpenCensus)
- ❌ Vendor lock-in with proprietary agents
- ❌ Different SDKs for different languages
- ❌ Inconsistent data formats
- ❌ Hard to switch between observability backends

**With OpenTelemetry:**
- ✅ Single, unified standard
- ✅ Vendor-neutral instrumentation
- ✅ Consistent APIs across languages
- ✅ Standardized data formats
- ✅ Easy to switch backends (Jaeger, Zipkin, Datadog, etc.)

### Key Benefits

1. **Vendor Agnostic**: Instrument once, export anywhere
2. **Future Proof**: Industry standard backed by major vendors
3. **Automatic Instrumentation**: Auto-detect popular frameworks
4. **Context Propagation**: Track requests across services
5. **Rich Ecosystem**: Wide language and framework support

---

## Core Concepts

### 1. Traces

A **trace** represents the entire journey of a request through your system.

```
User Request → API Gateway → Auth Service → Database → Response
    |              |              |            |
    └──────────────┴──────────────┴────────────┘
                 ONE TRACE
```

**Real-world example:**
```
Trace ID: abc123
├─ Span: HTTP POST /auth/login (100ms)
│  ├─ Span: authenticate_user (80ms)
│  │  ├─ Span: database_query (40ms)
│  │  └─ Span: verify_password (35ms)
│  └─ Span: create_jwt_token (15ms)
```

### 2. Spans

A **span** represents a single unit of work within a trace.

```python
Span Attributes:
├─ Name: "POST /books"
├─ Trace ID: abc123
├─ Span ID: xyz789
├─ Parent Span ID: parent456
├─ Start Time: 2026-01-11T10:00:00Z
├─ End Time: 2026-01-11T10:00:00.150Z
├─ Duration: 150ms
├─ Status: OK
└─ Attributes:
   ├─ http.method: POST
   ├─ http.status_code: 201
   ├─ db.system: postgresql
   └─ user.id: 123
```

**Span Types:**
- **Root Span**: Entry point of the trace
- **Child Span**: Nested operation within a parent
- **Internal Span**: Internal function calls
- **External Span**: Calls to external services

### 3. Context Propagation

How traces flow across service boundaries:

```
Service A                    Service B
─────────────────────────────────────────────────
Request Headers:
  traceparent: 00-abc123-xyz789-01
       │         │    │      │     │
       │         │    │      │     └─ Flags
       │         │    │      └─ Parent Span ID
       │         │    └─ Trace ID
       │         └─ Version
       │
       ↓
Both services share the same Trace ID
```

**Context propagation ensures:**
- Same trace ID across all services
- Parent-child relationships maintained
- End-to-end visibility

### 4. Instrumentation

Two types of instrumentation:

#### Automatic (Auto-instrumentation)
```python
# Automatically instruments popular libraries
- FastAPI
- SQLAlchemy
- Redis
- HTTP clients (requests, httpx)
- PostgreSQL drivers
```

#### Manual (Custom spans)
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_payment") as span:
    span.set_attribute("amount", 99.99)
    span.set_attribute("currency", "USD")
    # Your business logic here
```

### 5. Exporters

Exporters send telemetry data to backends:

```
Your App → OpenTelemetry SDK → Exporter → Backend
                                    ├─ Jaeger
                                    ├─ Zipkin
                                    ├─ Prometheus
                                    ├─ Datadog
                                    ├─ New Relic
                                    └─ Any OTLP receiver
```

---

## OpenTelemetry Architecture

```
┌────────────────────────────────────────────────────────┐
│                 Your Application                        │
├────────────────────────────────────────────────────────┤
│  OpenTelemetry API (Instrument your code)              │
├────────────────────────────────────────────────────────┤
│  OpenTelemetry SDK (Process and sample data)           │
│  ├─ Tracer Provider                                    │
│  ├─ Meter Provider (Metrics)                           │
│  └─ Logger Provider                                    │
├────────────────────────────────────────────────────────┤
│  Instrumentation Libraries                             │
│  ├─ FastAPI Auto-instrumentation                       │
│  ├─ SQLAlchemy Auto-instrumentation                    │
│  ├─ Redis Auto-instrumentation                         │
│  └─ Requests/HTTPX Auto-instrumentation                │
├────────────────────────────────────────────────────────┤
│  Exporters                                             │
│  ├─ OTLP Exporter (OpenTelemetry Protocol)            │
│  ├─ Jaeger Exporter                                   │
│  ├─ Zipkin Exporter                                   │
│  └─ Console Exporter (for debugging)                  │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│  OpenTelemetry Collector (Optional)                    │
│  ├─ Receives telemetry data                           │
│  ├─ Processes (filtering, batching, sampling)          │
│  ├─ Exports to multiple backends                       │
│  └─ Reduces backend load                              │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│  Backend (Choose one or many)                          │
│  ├─ Jaeger (Tracing)                                  │
│  ├─ Prometheus (Metrics)                              │
│  ├─ Grafana Loki (Logs)                               │
│  ├─ Elastic APM                                       │
│  └─ Commercial (Datadog, New Relic, etc.)             │
└────────────────────────────────────────────────────────┘
```

---

## Distributed Tracing Explained

### What is Distributed Tracing?

Tracking a request as it flows through multiple services in a microservices architecture.

### Example: Book Store API Request Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User: POST /books (Create a new book)                       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Span 1: HTTP POST /books                                    │
│ Service: FastAPI                                            │
│ Duration: 245ms                                             │
│ Status: 201 Created                                         │
└─────────────────────────────────────────────────────────────┘
    │
    ├─→ ┌───────────────────────────────────────────────────┐
    │   │ Span 2: authenticate_user                         │
    │   │ Duration: 85ms                                    │
    │   └───────────────────────────────────────────────────┘
    │       │
    │       └─→ ┌───────────────────────────────────────────┐
    │           │ Span 3: SELECT FROM users                 │
    │           │ Database: PostgreSQL                       │
    │           │ Duration: 40ms                            │
    │           └───────────────────────────────────────────┘
    │
    ├─→ ┌───────────────────────────────────────────────────┐
    │   │ Span 4: validate_book_data                        │
    │   │ Duration: 5ms                                     │
    │   └───────────────────────────────────────────────────┘
    │
    ├─→ ┌───────────────────────────────────────────────────┐
    │   │ Span 5: INSERT INTO books                         │
    │   │ Database: PostgreSQL                               │
    │   │ Duration: 120ms                                   │
    │   └───────────────────────────────────────────────────┘
    │
    └─→ ┌───────────────────────────────────────────────────┐
        │ Span 6: cache_invalidation                        │
        │ Service: Redis                                     │
        │ Duration: 25ms                                    │
        └───────────────────────────────────────────────────┘

Total Time: 245ms
Bottleneck: Database INSERT (120ms) - 49% of total time
```

### What You Can See

1. **Request Path**: Exact flow through your system
2. **Timing**: Where time is spent
3. **Bottlenecks**: Slow operations highlighted
4. **Errors**: Where failures occur
5. **Dependencies**: Service interactions
6. **Database Queries**: SQL performance
7. **External Calls**: API latency

---

## Jaeger - Distributed Tracing Backend

### What is Jaeger?

**Jaeger** is an open-source, end-to-end distributed tracing system originally developed by Uber Technologies and donated to CNCF.

### Jaeger Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Jaeger Components                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐                                       │
│  │  Jaeger      │ ← Receives traces from your app       │
│  │  Collector   │                                       │
│  └──────┬───────┘                                       │
│         │                                                │
│         ↓                                                │
│  ┌──────────────┐                                       │
│  │  Storage     │ ← Stores traces (Memory/Cassandra/    │
│  │              │   Elasticsearch/BadgerDB)             │
│  └──────┬───────┘                                       │
│         │                                                │
│         ↓                                                │
│  ┌──────────────┐                                       │
│  │  Jaeger      │ ← Query and display traces            │
│  │  Query UI    │   (Web interface)                     │
│  └──────────────┘                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Jaeger UI Features

1. **Trace Search**
   - Find traces by service, operation, tags
   - Filter by duration, time range
   - Advanced query options

2. **Trace Visualization**
   - Waterfall view of spans
   - Gantt chart timeline
   - Service dependency graph

3. **Service Performance**
   - Request rate
   - Error rate
   - Latency percentiles (p50, p95, p99)

4. **Comparison**
   - Compare multiple traces
   - Identify anomalies
   - Performance regression detection

### Jaeger vs Other Tracing Tools

| Feature | Jaeger | Zipkin | Tempo | Datadog |
|---------|--------|--------|-------|---------|
| **Cost** | Free | Free | Free | Paid |
| **Backend** | Self-hosted | Self-hosted | Self-hosted | Cloud |
| **Storage** | Multiple | Multiple | S3/GCS | Cloud |
| **UI** | Excellent | Good | Via Grafana | Excellent |
| **CNCF** | ✅ | ❌ | ✅ | ❌ |
| **Sampling** | ✅ | ✅ | ✅ | ✅ |

---

## Key Terminology

### Observability Terms

- **Trace**: Complete journey of a request
- **Span**: Single unit of work
- **Trace ID**: Unique identifier for a trace
- **Span ID**: Unique identifier for a span
- **Parent Span**: Span that initiated a child span
- **Root Span**: First span in a trace (no parent)
- **Attributes**: Key-value metadata on spans
- **Events**: Timestamped logs within a span
- **Status**: Outcome of a span (OK, ERROR)
- **Context**: Propagation of trace information

### Sampling Terms

- **Head Sampling**: Decision made at trace start
- **Tail Sampling**: Decision after trace completion
- **Sampling Rate**: Percentage of traces to capture
- **Adaptive Sampling**: Dynamic rate adjustment

### Performance Terms

- **Latency**: Time to complete a request
- **Throughput**: Requests per second
- **p50/p95/p99**: Latency percentiles
- **Span Duration**: Time a span took
- **Critical Path**: Longest path through a trace

---

## Common Use Cases

### 1. Performance Debugging

**Scenario**: API endpoint is slow

**With Tracing:**
```
✅ Identify exact slow operation (DB query, external API)
✅ See if it's consistent or intermittent
✅ Compare fast vs slow requests
✅ Find optimization opportunities
```

### 2. Error Investigation

**Scenario**: Users reporting intermittent errors

**With Tracing:**
```
✅ Find all failed traces
✅ See error propagation path
✅ Identify root cause service
✅ Correlate errors with specific conditions
```

### 3. Dependency Mapping

**Scenario**: Understanding service interactions

**With Tracing:**
```
✅ Visualize service dependency graph
✅ Find unused dependencies
✅ Identify circular dependencies
✅ Plan service decomposition
```

### 4. SLA Monitoring

**Scenario**: Tracking performance SLAs

**With Tracing:**
```
✅ Monitor p95, p99 latencies
✅ Set up alerts for SLA violations
✅ Track performance trends over time
✅ Identify degradation before users notice
```

### 5. Capacity Planning

**Scenario**: Preparing for traffic growth

**With Tracing:**
```
✅ Identify bottleneck services
✅ Estimate resource requirements
✅ Plan horizontal/vertical scaling
✅ Optimize before scaling
```

---

## Best Practices

### 1. Span Naming
```python
# ❌ Bad
span.name = "function_1"

# ✅ Good
span.name = "GET /api/books"
span.name = "database_query_users"
span.name = "validate_book_data"
```

### 2. Add Meaningful Attributes
```python
# ❌ Bad
span.set_attribute("id", 123)

# ✅ Good
span.set_attribute("user.id", 123)
span.set_attribute("book.isbn", "978-0-123456-78-9")
span.set_attribute("http.status_code", 200)
span.set_attribute("db.operation", "SELECT")
```

### 3. Sampling Strategy
```python
# Production: Sample 10% of traces
sampler = TraceIdRatioBased(0.1)

# Development: Sample 100%
sampler = AlwaysOn()

# High-traffic: Sample errors + slow requests
sampler = ParentBasedTraceIdRatioBased(0.01)
```

### 4. Avoid Over-instrumentation
```python
# ❌ Too granular
with tracer.start_span("add_numbers"):
    result = a + b

# ✅ Appropriate level
with tracer.start_span("process_payment"):
    # Multiple operations
```

### 5. Handle Errors Properly
```python
try:
    result = risky_operation()
    span.set_status(Status(StatusCode.OK))
except Exception as e:
    span.set_status(Status(StatusCode.ERROR, str(e)))
    span.record_exception(e)
    raise
```

---

## Security & Privacy Considerations

### Data to Avoid in Spans

```python
# ❌ NEVER include:
span.set_attribute("password", user.password)
span.set_attribute("credit_card", card_number)
span.set_attribute("ssn", social_security)
span.set_attribute("token", jwt_token)

# ✅ Safe to include:
span.set_attribute("user.id", user.id)
span.set_attribute("payment.status", "success")
span.set_attribute("http.method", "POST")
```

### Sampling for Sensitive Operations
- Higher sampling for non-sensitive endpoints
- Lower/zero sampling for auth/payment flows
- Use attribute filtering in exporters

---

## OpenTelemetry Ecosystem

### Official Libraries

- **Python**: `opentelemetry-api`, `opentelemetry-sdk`
- **JavaScript**: `@opentelemetry/api`, `@opentelemetry/sdk-node`
- **Go**: `go.opentelemetry.io/otel`
- **Java**: `io.opentelemetry:opentelemetry-api`
- **C#**: `OpenTelemetry` NuGet packages

### Auto-instrumentation Libraries (Python)

- **FastAPI**: `opentelemetry-instrumentation-fastapi`
- **SQLAlchemy**: `opentelemetry-instrumentation-sqlalchemy`
- **Redis**: `opentelemetry-instrumentation-redis`
- **Requests**: `opentelemetry-instrumentation-requests`
- **psycopg2**: `opentelemetry-instrumentation-psycopg2`

### Backends Compatible with OTLP

- Jaeger
- Zipkin
- Grafana Tempo
- Elastic APM
- Datadog
- New Relic
- Honeycomb
- Lightstep
- AWS X-Ray
- Google Cloud Trace

---

## Resources

### Official Documentation
- [OpenTelemetry.io](https://opentelemetry.io/)
- [Python OpenTelemetry Docs](https://opentelemetry.io/docs/languages/python/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [CNCF OpenTelemetry](https://www.cncf.io/projects/opentelemetry/)

### Learning Resources
- [OpenTelemetry Demo](https://github.com/open-telemetry/opentelemetry-demo)
- [Distributed Tracing Guide](https://opentelemetry.io/docs/concepts/observability-primer/)
- [Jaeger Tutorial](https://www.jaegertracing.io/docs/latest/getting-started/)

### Community
- [OpenTelemetry Slack](https://cloud-native.slack.com/)
- [GitHub Discussions](https://github.com/open-telemetry/opentelemetry-python/discussions)
- [CNCF Community](https://www.cncf.io/community/)

---

## Quick Reference

### Trace Context Propagation

```
HTTP Headers (W3C Trace Context):
  traceparent: 00-{trace-id}-{span-id}-{flags}
  tracestate: vendor-specific-data
```

### Common Status Codes

- `StatusCode.UNSET`: Default, no error
- `StatusCode.OK`: Explicitly successful
- `StatusCode.ERROR`: Operation failed

### Span Kinds

- `INTERNAL`: Default, internal operation
- `SERVER`: Server handling a request
- `CLIENT`: Client making a request
- `PRODUCER`: Message producer
- `CONSUMER`: Message consumer

### Sampling Decisions

- `RECORD_AND_SAMPLE`: Include in trace and export
- `RECORD`: Include but don't export
- `DROP`: Don't record or export

---

**Next Steps:** See [OTEL_IMPLEMENTATION_GUIDE.md](OTEL_IMPLEMENTATION_GUIDE.md) for hands-on implementation in this FastAPI application.
