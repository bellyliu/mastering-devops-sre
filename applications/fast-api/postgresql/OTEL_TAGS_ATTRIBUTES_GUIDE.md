# OpenTelemetry Tags & Attributes - Production Observability Guide

## Table of Contents

1. [What Are Tags/Attributes?](#what-are-tagsattributes)
2. [Automatic vs Manual Attributes](#automatic-vs-manual-attributes)
3. [Production Use Cases](#production-use-cases)
4. [Standard Attribute Conventions](#standard-attribute-conventions)
5. [Querying & Filtering in Jaeger](#querying--filtering-in-jaeger)
6. [Production Tagging Strategies](#production-tagging-strategies)
7. [Real-World Examples](#real-world-examples)
8. [Best Practices](#best-practices)
9. [Implementation Examples](#implementation-examples)

---

## What Are Tags/Attributes?

**Attributes** (also called **tags** or **labels**) are key-value pairs attached to spans that provide context and metadata about operations.

### Structure

```python
span.set_attribute("key", "value")
```

### Data Types

```python
# String
span.set_attribute("user.role", "admin")

# Integer
span.set_attribute("http.status_code", 200)

# Boolean
span.set_attribute("cache.hit", True)

# Float
span.set_attribute("response.size_mb", 2.5)

# Arrays (lists)
span.set_attribute("regions", ["us-east-1", "eu-west-1"])
```

### Why Attributes Matter

```
Without Attributes:
  POST /api/books (150ms) ← Limited information

With Attributes:
  POST /api/books (150ms)
  ├─ http.method: POST
  ├─ http.status_code: 201
  ├─ user.id: 12345
  ├─ user.role: premium
  ├─ book.category: technology
  ├─ db.system: postgresql
  ├─ db.statement: INSERT INTO books...
  ├─ cache.hit: false
  └─ region: us-east-1
  
  ✅ Can filter: All requests from premium users
  ✅ Can analyze: Cache hit rates by region
  ✅ Can debug: Slow queries for specific categories
```

---

## Automatic vs Manual Attributes

### Automatically Set Attributes

These are added by OpenTelemetry instrumentation libraries **without any code changes**.

#### 1. HTTP/FastAPI Auto-Instrumentation

```yaml
# Automatic attributes from opentelemetry-instrumentation-fastapi
http.method: "POST"
http.route: "/books/"
http.url: "http://localhost:8000/books/"
http.scheme: "http"
http.host: "localhost:8000"
http.target: "/books/"
http.flavor: "1.1"
http.status_code: 201
http.user_agent: "curl/7.68.0"
net.peer.ip: "172.17.0.1"
net.peer.port: 45678
```

#### 2. Database (SQLAlchemy/psycopg2) Auto-Instrumentation

```yaml
# Automatic attributes from opentelemetry-instrumentation-sqlalchemy
db.system: "postgresql"
db.name: "bookstore"
db.user: "fastapi"
db.statement: "INSERT INTO books (title, author, isbn, owner_id) VALUES (?, ?, ?, ?)"
db.operation: "INSERT"
db.sql.table: "books"
```

#### 3. Redis Auto-Instrumentation

```yaml
# Automatic attributes from opentelemetry-instrumentation-redis
db.system: "redis"
db.redis.database_index: 0
db.statement: "GET book:123"
net.peer.name: "redis"
net.peer.port: 6379
```

#### 4. Resource Attributes (Service-Level)

```yaml
# Set once in app/tracing.py
service.name: "bookstore-api"
service.version: "1.0.0"
service.namespace: "production"
deployment.environment: "production"
service.instance.id: "bookstore-api-pod-abc123"
```

### Manually Set Attributes

These are added **explicitly in your code** for business context.

```python
from opentelemetry import trace

current_span = trace.get_current_span()

# Business context
current_span.set_attribute("user.id", current_user.id)
current_span.set_attribute("user.role", current_user.role)
current_span.set_attribute("user.subscription", "premium")

# Domain-specific
current_span.set_attribute("book.category", book.category)
current_span.set_attribute("book.price", book.price)
current_span.set_attribute("book.isbn", book.isbn)

# Operational
current_span.set_attribute("cache.hit", cache_hit)
current_span.set_attribute("retry.count", retry_count)
current_span.set_attribute("feature.flag.new_ui", True)
```

---

## Production Use Cases

### 1. Error Debugging & Root Cause Analysis

**Scenario**: Users reporting intermittent 500 errors

**Attributes to Add**:
```python
span.set_attribute("user.id", user_id)
span.set_attribute("user.account_age_days", account_age)
span.set_attribute("request.id", request_id)
span.set_attribute("db.connection.pool.size", pool_size)
span.set_attribute("external.api.timeout", timeout_seconds)
```

**How to Use in Jaeger**:
```
1. Search: http.status_code=500
2. Filter by: service.version="1.2.3" (new deployment)
3. Group by: user.account_age_days
4. Result: All errors from accounts < 7 days old
   → Root cause: New user onboarding flow bug
```

---

### 2. Performance Optimization

**Scenario**: Identify slow requests for specific user segments

**Attributes to Add**:
```python
span.set_attribute("user.tier", "free|premium|enterprise")
span.set_attribute("user.region", "us-east-1")
span.set_attribute("cache.strategy", "redis|memory|none")
span.set_attribute("db.query.complexity", "simple|complex")
span.set_attribute("result.count", len(results))
```

**Jaeger Query**:
```
Service: bookstore-api
Operation: GET /books/
Tags: user.tier=free duration>500ms
Result: Free tier queries taking >500ms
   → Optimize: Add pagination limits for free users
```

---

### 3. A/B Testing & Feature Flags

**Scenario**: Measure performance impact of new feature

**Attributes to Add**:
```python
span.set_attribute("experiment.id", "new_search_algorithm")
span.set_attribute("experiment.variant", "control|treatment")
span.set_attribute("feature.recommendation_engine", enabled)
```

**Analysis**:
```sql
-- Compare latency between variants
Control group (old algorithm): p95 = 120ms
Treatment group (new algorithm): p95 = 85ms
✅ Deploy new algorithm (29% improvement)
```

---

### 4. Business Metrics & Analytics

**Scenario**: Track revenue-generating operations

**Attributes to Add**:
```python
span.set_attribute("transaction.type", "purchase|refund")
span.set_attribute("transaction.amount", 99.99)
span.set_attribute("transaction.currency", "USD")
span.set_attribute("payment.method", "credit_card")
span.set_attribute("payment.gateway", "stripe")
span.set_attribute("cart.item_count", 3)
span.set_attribute("discount.applied", True)
span.set_attribute("discount.code", "SUMMER2026")
```

**Observability**:
- Track payment gateway failures by provider
- Correlate discount codes with checkout duration
- Identify high-value transactions with errors
- Monitor refund request patterns

---

### 5. SLA Monitoring & Alerting

**Scenario**: Track SLA compliance per customer tier

**Attributes to Add**:
```python
span.set_attribute("customer.id", customer_id)
span.set_attribute("customer.sla_tier", "gold|silver|bronze")
span.set_attribute("customer.contract_id", contract_id)
span.set_attribute("sla.target_latency_ms", 100)
```

**Alert Rules**:
```yaml
# Alert if Gold tier SLA violated
Query: service.name=bookstore-api 
       customer.sla_tier=gold 
       duration>100ms
Threshold: > 5% of requests
Action: Page on-call engineer
```

---

### 6. Security & Compliance

**Scenario**: Audit trail for sensitive operations

**Attributes to Add**:
```python
span.set_attribute("security.action", "access_pii")
span.set_attribute("security.resource", "user_profile")
span.set_attribute("security.principal", admin_user_id)
span.set_attribute("compliance.gdpr_scope", True)
span.set_attribute("audit.reason", "customer_support_request")
span.set_attribute("data.classification", "confidential")
```

**Compliance Queries**:
```
# Find all PII access in last 30 days
security.action=access_pii compliance.gdpr_scope=true

# Audit admin actions
security.principal=admin_* security.action=modify_user_data
```

---

### 7. Multi-Tenancy & Customer Isolation

**Scenario**: Track performance per tenant

**Attributes to Add**:
```python
span.set_attribute("tenant.id", tenant_id)
span.set_attribute("tenant.name", "acme-corp")
span.set_attribute("tenant.plan", "enterprise")
span.set_attribute("tenant.region", "eu-central-1")
span.set_attribute("tenant.quota.limit", 10000)
span.set_attribute("tenant.quota.used", 8500)
```

**Use Cases**:
- Identify noisy neighbors (high request volume tenants)
- Per-tenant performance SLAs
- Resource utilization tracking
- Quota enforcement monitoring

---

### 8. Infrastructure & Deployment Tracking

**Scenario**: Canary deployment monitoring

**Attributes to Add**:
```python
span.set_attribute("deployment.id", "v2.3.1-canary")
span.set_attribute("deployment.strategy", "blue-green|canary")
span.set_attribute("instance.id", pod_name)
span.set_attribute("instance.zone", "us-east-1a")
span.set_attribute("cluster.name", "prod-cluster-1")
span.set_attribute("node.type", "c5.2xlarge")
```

**Deployment Validation**:
```
# Compare old vs new deployment
Old: deployment.id=v2.3.0 → error_rate=0.1%
New: deployment.id=v2.3.1-canary → error_rate=2.5%
🚨 Rollback triggered
```

---

## Standard Attribute Conventions

OpenTelemetry defines **semantic conventions** for consistent naming.

### HTTP Attributes

```python
# Standardized (OpenTelemetry Semantic Conventions)
span.set_attribute("http.method", "POST")
span.set_attribute("http.status_code", 201)
span.set_attribute("http.route", "/books/{id}")
span.set_attribute("http.client_ip", "192.168.1.1")
span.set_attribute("http.request.header.content_type", "application/json")
span.set_attribute("http.response.header.content_length", 1024)
```

**Reference**: [OpenTelemetry HTTP Conventions](https://opentelemetry.io/docs/specs/semconv/http/http-spans/)

### Database Attributes

```python
# Standardized
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.name", "bookstore")
span.set_attribute("db.operation", "SELECT")
span.set_attribute("db.sql.table", "books")
span.set_attribute("db.user", "fastapi")
span.set_attribute("db.connection_string", "postgresql://localhost:5432")

# Performance
span.set_attribute("db.rows_affected", 5)
span.set_attribute("db.statement", "SELECT * FROM books WHERE category = ?")
```

**Reference**: [OpenTelemetry Database Conventions](https://opentelemetry.io/docs/specs/semconv/database/database-spans/)

### User & Session Attributes

```python
# Custom but common patterns
span.set_attribute("enduser.id", "user_12345")
span.set_attribute("enduser.role", "admin")
span.set_attribute("enduser.scope", "read:books write:books")
span.set_attribute("session.id", session_id)
span.set_attribute("session.duration_seconds", 3600)
```

### Cloud & Infrastructure Attributes

```python
# AWS
span.set_attribute("cloud.provider", "aws")
span.set_attribute("cloud.region", "us-east-1")
span.set_attribute("cloud.availability_zone", "us-east-1a")
span.set_attribute("cloud.account.id", "123456789012")

# Kubernetes
span.set_attribute("k8s.cluster.name", "prod-cluster")
span.set_attribute("k8s.namespace.name", "bookstore")
span.set_attribute("k8s.pod.name", "bookstore-api-7d9f8c6b5-xyz")
span.set_attribute("k8s.deployment.name", "bookstore-api")
span.set_attribute("k8s.container.name", "api")
```

**Reference**: [OpenTelemetry Cloud Conventions](https://opentelemetry.io/docs/specs/semconv/cloud/)

---

## Querying & Filtering in Jaeger

### Basic Tag Search

```
1. Open Jaeger UI: http://localhost:16686
2. Select Service: bookstore-api
3. Add Tags:
   - http.status_code=500
   - user.tier=premium
   - duration>1000ms
4. Click "Find Traces"
```

### Advanced Tag Queries

#### Find Slow Premium User Requests
```
Service: bookstore-api
Tags: user.tier=premium duration>500ms
Lookback: 1h
Limit: 100
```

#### Find Database Errors
```
Service: bookstore-api
Tags: db.system=postgresql error=true
Operation: INSERT /books/
```

#### Find Cache Misses
```
Service: bookstore-api
Tags: cache.hit=false
Operation: GET /books/{id}
```

#### Find Specific User Journey
```
Service: bookstore-api
Tags: user.id=12345
Lookback: 24h
```

### Tag Aggregation (Via Jaeger API)

Jaeger doesn't have built-in aggregation UI, but you can query via API:

```bash
# Get all unique values for a tag
curl "http://localhost:16686/api/traces?service=bookstore-api&tag=user.tier"

# Export traces with specific tags to JSON
curl "http://localhost:16686/api/traces?service=bookstore-api&tag=http.status_code:500" \
  | jq '.data[].spans[].tags'
```

### Exporting to Analytics Tools

For advanced analytics, export Jaeger data to:

- **Grafana**: Visualize metrics from traces
- **Elasticsearch**: Full-text search and aggregations
- **Prometheus**: Convert span attributes to metrics
- **Custom scripts**: Python/Go scripts to analyze JSON exports

---

## Production Tagging Strategies

### 1. Layered Tagging Strategy

```python
# Layer 1: Infrastructure (Resource Attributes)
resource = Resource(attributes={
    "service.name": "bookstore-api",
    "service.version": os.getenv("VERSION", "1.0.0"),
    "deployment.environment": os.getenv("ENV", "production"),
    "cloud.provider": "aws",
    "cloud.region": os.getenv("AWS_REGION", "us-east-1"),
    "k8s.pod.name": os.getenv("HOSTNAME"),
})

# Layer 2: Request Context (Auto-instrumentation)
# Automatically added: http.*, db.*, net.*

# Layer 3: Business Context (Manual)
span.set_attribute("user.id", user.id)
span.set_attribute("user.tier", user.subscription_tier)
span.set_attribute("tenant.id", tenant.id)

# Layer 4: Performance Metrics (Manual)
span.set_attribute("cache.hit", cache_hit)
span.set_attribute("db.pool.size", db_pool_size)
span.set_attribute("result.count", len(results))

# Layer 5: Feature Flags (Manual)
span.set_attribute("feature.new_ui", feature_flags.new_ui)
span.set_attribute("experiment.variant", get_experiment_variant())
```

### 2. Cardinality Management

**Problem**: Too many unique tag values = high storage costs

```python
# ❌ BAD: High cardinality (millions of unique values)
span.set_attribute("user.email", user.email)  # Unique per user
span.set_attribute("timestamp.exact", datetime.now().isoformat())
span.set_attribute("request.body", json.dumps(request_body))  # Unbounded

# ✅ GOOD: Low cardinality (bounded values)
span.set_attribute("user.id_hash", hash(user.id) % 1000)  # 0-999
span.set_attribute("timestamp.hour", datetime.now().strftime("%Y-%m-%d-%H"))
span.set_attribute("request.size_bucket", get_size_bucket(len(request_body)))
```

**Cardinality Guidelines**:
- **Low**: < 100 unique values (ideal)
- **Medium**: 100-10,000 unique values (acceptable)
- **High**: > 10,000 unique values (avoid for frequently used tags)

### 3. Namespace Conventions

Use dot notation for hierarchical organization:

```python
# User namespace
span.set_attribute("user.id", 12345)
span.set_attribute("user.role", "admin")
span.set_attribute("user.tier", "premium")
span.set_attribute("user.region", "us-east")

# Transaction namespace
span.set_attribute("transaction.id", "tx_abc123")
span.set_attribute("transaction.type", "purchase")
span.set_attribute("transaction.amount", 99.99)
span.set_attribute("transaction.currency", "USD")

# Feature namespace
span.set_attribute("feature.recommendation", True)
span.set_attribute("feature.ab_test.variant", "B")
span.set_attribute("feature.beta_access", False)
```

### 4. Conditional Tagging

Add detailed tags only when needed:

```python
# Always add
span.set_attribute("user.id", user.id)

# Add only on errors
if span.is_recording() and error_occurred:
    span.set_attribute("error.type", type(error).__name__)
    span.set_attribute("error.message", str(error))
    span.set_attribute("error.stack_trace", traceback.format_exc())

# Add only for slow requests
if duration > 1000:
    span.set_attribute("slow_query.sql", query)
    span.set_attribute("slow_query.params", params)
    span.set_attribute("slow_query.explain_plan", explain_plan)

# Add sampling for high-volume operations
if should_sample(sampling_rate=0.01):  # 1%
    span.set_attribute("detailed.metrics", get_detailed_metrics())
```

---

## Real-World Examples

### Example 1: E-commerce Checkout Flow

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

def process_checkout(cart, user, payment_info):
    with tracer.start_as_current_span("checkout.process") as span:
        # User context
        span.set_attribute("user.id", user.id)
        span.set_attribute("user.tier", user.subscription_tier)
        span.set_attribute("user.lifetime_value", user.lifetime_value)
        
        # Cart context
        span.set_attribute("cart.item_count", len(cart.items))
        span.set_attribute("cart.total_amount", cart.total)
        span.set_attribute("cart.currency", cart.currency)
        span.set_attribute("cart.has_discount", cart.discount_code is not None)
        
        # Business context
        span.set_attribute("checkout.channel", "web")  # web|mobile|api
        span.set_attribute("checkout.country", user.country)
        span.set_attribute("checkout.payment_method", payment_info.method)
        
        try:
            # Validate inventory
            with tracer.start_as_current_span("checkout.validate_inventory") as inv_span:
                inventory_ok = validate_inventory(cart)
                inv_span.set_attribute("inventory.sufficient", inventory_ok)
                
                if not inventory_ok:
                    inv_span.add_event("Inventory insufficient")
                    span.set_status(Status(StatusCode.ERROR, "Out of stock"))
                    return None
            
            # Process payment
            with tracer.start_as_current_span("checkout.process_payment") as pay_span:
                pay_span.set_attribute("payment.amount", cart.total)
                pay_span.set_attribute("payment.gateway", "stripe")
                
                payment_result = charge_payment(payment_info, cart.total)
                
                pay_span.set_attribute("payment.transaction_id", payment_result.tx_id)
                pay_span.set_attribute("payment.status", payment_result.status)
                
                if payment_result.declined:
                    pay_span.set_attribute("payment.decline_reason", payment_result.reason)
                    pay_span.add_event("Payment declined")
                    span.set_status(Status(StatusCode.ERROR, "Payment failed"))
                    return None
            
            # Create order
            with tracer.start_as_current_span("checkout.create_order") as order_span:
                order = create_order(cart, user, payment_result)
                order_span.set_attribute("order.id", order.id)
                order_span.set_attribute("order.fulfillment_method", "standard_shipping")
                order_span.add_event("Order created successfully")
            
            # Track conversion
            span.set_attribute("conversion.completed", True)
            span.set_attribute("conversion.revenue", cart.total)
            span.add_event("Checkout completed", {
                "order_id": order.id,
                "revenue": cart.total
            })
            
            span.set_status(Status(StatusCode.OK))
            return order
            
        except Exception as e:
            span.set_attribute("error.type", type(e).__name__)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
```

**What You Can Analyze**:
- Checkout completion rate by payment method
- Average cart value by user tier
- Payment decline reasons by country
- Inventory issues causing checkout failures
- Time spent in each checkout step
- Revenue per successful checkout

---

### Example 2: API Rate Limiting & Quota Tracking

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

async def api_endpoint_with_rate_limit(request, user):
    with tracer.start_as_current_span("api.rate_limit_check") as span:
        # User context
        span.set_attribute("user.id", user.id)
        span.set_attribute("user.api_tier", user.api_tier)  # free|pro|enterprise
        
        # Rate limit context
        rate_limit = get_rate_limit(user.api_tier)
        current_usage = get_current_usage(user.id)
        
        span.set_attribute("rate_limit.limit", rate_limit.max_requests)
        span.set_attribute("rate_limit.window", rate_limit.window_seconds)
        span.set_attribute("rate_limit.current_usage", current_usage)
        span.set_attribute("rate_limit.remaining", rate_limit.max_requests - current_usage)
        span.set_attribute("rate_limit.percentage_used", 
                          (current_usage / rate_limit.max_requests) * 100)
        
        # Check if rate limit exceeded
        if current_usage >= rate_limit.max_requests:
            span.set_attribute("rate_limit.exceeded", True)
            span.set_attribute("rate_limit.retry_after", rate_limit.reset_time)
            span.add_event("Rate limit exceeded")
            span.set_status(Status(StatusCode.ERROR, "Rate limit exceeded"))
            
            # Log for upgrade opportunities
            if user.api_tier == "free":
                span.set_attribute("upgrade.opportunity", True)
            
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        span.set_attribute("rate_limit.exceeded", False)
        increment_usage(user.id)
        
        # Warn if approaching limit
        if current_usage > rate_limit.max_requests * 0.8:
            span.add_event("Approaching rate limit", {
                "threshold": "80%",
                "current": current_usage,
                "limit": rate_limit.max_requests
            })
        
        return await process_request(request)
```

**What You Can Analyze**:
- Users hitting rate limits (upgrade candidates)
- Rate limit utilization by tier
- Peak usage times
- API abuse patterns
- Upgrade conversion tracking

---

### Example 3: Multi-Region Request Routing

```python
from opentelemetry import trace
import time

tracer = trace.get_tracer(__name__)

def route_request_to_region(request, user):
    with tracer.start_as_current_span("routing.region_selection") as span:
        # Request metadata
        span.set_attribute("request.source_ip", request.client_ip)
        span.set_attribute("request.user_agent", request.user_agent)
        
        # User context
        span.set_attribute("user.id", user.id)
        span.set_attribute("user.home_region", user.preferred_region)
        span.set_attribute("user.data_residency", user.data_residency)  # EU, US, APAC
        
        # Determine optimal region
        start_time = time.time()
        
        regions = ["us-east-1", "eu-west-1", "ap-southeast-1"]
        latencies = measure_region_latencies(request.client_ip, regions)
        
        span.set_attribute("routing.candidates", len(regions))
        span.set_attribute("routing.latency_check_ms", (time.time() - start_time) * 1000)
        
        # Select based on latency + data residency
        selected_region = select_optimal_region(
            latencies, 
            user.data_residency,
            user.preferred_region
        )
        
        span.set_attribute("routing.selected_region", selected_region)
        span.set_attribute("routing.reason", get_selection_reason())
        span.set_attribute("routing.latency_to_region_ms", latencies[selected_region])
        
        # Performance metrics
        for region, latency in latencies.items():
            span.set_attribute(f"routing.latency.{region}_ms", latency)
        
        # Compliance
        if user.data_residency == "EU":
            span.set_attribute("compliance.gdpr_compliant", 
                             selected_region.startswith("eu-"))
        
        span.add_event("Region selected", {
            "region": selected_region,
            "latency_ms": latencies[selected_region]
        })
        
        return route_to_region(request, selected_region)
```

**What You Can Analyze**:
- Region selection distribution
- Cross-region latencies
- Data residency compliance
- User experience by geographic location
- Region failover patterns

---

## Best Practices

### ✅ DO

1. **Use Semantic Conventions**
   ```python
   # Standard names
   span.set_attribute("http.method", "POST")
   span.set_attribute("db.system", "postgresql")
   ```

2. **Keep Cardinality Low**
   ```python
   # Bounded values
   span.set_attribute("user.tier", "free|pro|enterprise")
   span.set_attribute("region", "us|eu|apac")
   ```

3. **Add Business Context**
   ```python
   span.set_attribute("user.subscription_status", "active")
   span.set_attribute("transaction.revenue", 99.99)
   ```

4. **Use Namespaces**
   ```python
   span.set_attribute("cache.hit", True)
   span.set_attribute("cache.provider", "redis")
   span.set_attribute("cache.ttl_seconds", 3600)
   ```

5. **Document Your Tags**
   ```python
   # Create a tags.yaml file
   tags:
     user.tier:
       type: string
       values: [free, pro, enterprise]
       purpose: Track user subscription level
   ```

### ❌ DON'T

1. **Don't Add PII**
   ```python
   # ❌ BAD
   span.set_attribute("user.email", "user@example.com")
   span.set_attribute("user.ssn", "123-45-6789")
   span.set_attribute("credit_card", "4111...")
   
   # ✅ GOOD
   span.set_attribute("user.id_hash", hash(user.email))
   span.set_attribute("user.country", "US")
   ```

2. **Don't Use High Cardinality**
   ```python
   # ❌ BAD
   span.set_attribute("timestamp.exact", datetime.now().isoformat())
   span.set_attribute("request.uuid", str(uuid.uuid4()))
   
   # ✅ GOOD
   span.set_attribute("timestamp.hour", "2026-01-14-15")
   span.set_attribute("request.batch_id", batch_id)
   ```

3. **Don't Add Large Values**
   ```python
   # ❌ BAD
   span.set_attribute("response.body", json.dumps(large_response))  # 10MB
   span.set_attribute("error.full_stack", full_stack_trace)  # 50KB
   
   # ✅ GOOD
   span.set_attribute("response.size_bytes", len(response_body))
   span.set_attribute("error.type", "ValueError")
   ```

4. **Don't Duplicate Auto-Instrumentation**
   ```python
   # ❌ BAD (already added by FastAPI instrumentation)
   span.set_attribute("http.method", request.method)
   span.set_attribute("http.status_code", response.status_code)
   
   # ✅ GOOD (add business context)
   span.set_attribute("user.id", current_user.id)
   span.set_attribute("book.category", book.category)
   ```

---

## Implementation Examples

### Complete FastAPI Example with Production Tags

```python
# app/routers/books.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from app import crud, schemas, database
from app.dependencies import get_current_user
import time

router = APIRouter()
tracer = trace.get_tracer(__name__)

@router.post("/", response_model=schemas.Book, status_code=201)
async def create_book(
    request: Request,
    book: schemas.BookCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Create a book with comprehensive tracing."""
    
    current_span = trace.get_current_span()
    start_time = time.time()
    
    # ===== RESOURCE ATTRIBUTES (from request) =====
    current_span.set_attribute("http.client_ip", request.client.host)
    current_span.set_attribute("http.user_agent", request.headers.get("user-agent", "unknown"))
    
    # ===== USER CONTEXT =====
    current_span.set_attribute("user.id", current_user.id)
    current_span.set_attribute("user.username", current_user.username)
    current_span.set_attribute("user.is_active", current_user.is_active)
    
    # Derive user tier (example)
    user_book_count = crud.get_user_book_count(db, current_user.id)
    user_tier = "premium" if user_book_count > 10 else "free"
    current_span.set_attribute("user.tier", user_tier)
    current_span.set_attribute("user.book_count", user_book_count)
    
    # ===== BUSINESS CONTEXT =====
    current_span.set_attribute("book.title", book.title)
    current_span.set_attribute("book.author", book.author)
    current_span.set_attribute("book.category", book.category or "uncategorized")
    current_span.set_attribute("book.price", float(book.price))
    current_span.set_attribute("book.year", book.year)
    
    # Price bucket for analysis
    price_bucket = "low" if book.price < 10 else "medium" if book.price < 30 else "high"
    current_span.set_attribute("book.price_bucket", price_bucket)
    
    # ===== VALIDATION =====
    with tracer.start_as_current_span("validation.check_book_data") as val_span:
        validation_start = time.time()
        
        if len(book.title) < 3:
            val_span.add_event("Validation failed", {"reason": "title_too_short"})
            val_span.set_attribute("validation.result", "failed")
            val_span.set_attribute("validation.error", "title_too_short")
            current_span.set_status(Status(StatusCode.ERROR, "Validation failed"))
            raise HTTPException(status_code=400, detail="Title too short")
        
        # Check for duplicate ISBN
        existing = crud.get_book_by_isbn(db, book.isbn)
        val_span.set_attribute("validation.duplicate_check", True)
        val_span.set_attribute("validation.duplicate_found", existing is not None)
        
        if existing:
            val_span.add_event("Duplicate ISBN detected", {"isbn": book.isbn})
            val_span.set_attribute("validation.result", "failed")
            current_span.set_status(Status(StatusCode.ERROR, "Duplicate ISBN"))
            raise HTTPException(status_code=409, detail="Book with this ISBN exists")
        
        val_span.set_attribute("validation.result", "passed")
        val_span.set_attribute("validation.duration_ms", (time.time() - validation_start) * 1000)
    
    # ===== DATABASE OPERATION =====
    try:
        db_book = crud.create_book(db=db, book=book, user_id=current_user.id)
        
        # ===== SUCCESS METRICS =====
        current_span.set_attribute("book.id", db_book.id)
        current_span.set_attribute("operation.result", "success")
        current_span.set_attribute("db.rows_affected", 1)
        
        # ===== PERFORMANCE =====
        total_duration = (time.time() - start_time) * 1000
        current_span.set_attribute("operation.total_duration_ms", total_duration)
        
        # Performance bucket
        if total_duration > 500:
            current_span.add_event("Slow operation detected", {
                "duration_ms": total_duration,
                "threshold": 500
            })
            current_span.set_attribute("performance.slow", True)
        
        current_span.add_event("Book created successfully", {
            "book_id": db_book.id,
            "duration_ms": total_duration
        })
        
        return db_book
        
    except Exception as e:
        # ===== ERROR TRACKING =====
        current_span.set_attribute("operation.result", "error")
        current_span.set_attribute("error.type", type(e).__name__)
        current_span.set_attribute("error.message", str(e))
        current_span.record_exception(e)
        current_span.set_status(Status(StatusCode.ERROR, str(e)))
        
        raise


@router.get("/", response_model=list[schemas.Book])
async def list_books(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    search: str = None,
    db: Session = Depends(database.get_db)
):
    """List books with comprehensive query tracking."""
    
    current_span = trace.get_current_span()
    
    # ===== QUERY PARAMETERS =====
    current_span.set_attribute("query.skip", skip)
    current_span.set_attribute("query.limit", min(limit, 100))  # Enforce max
    current_span.set_attribute("query.has_category_filter", category is not None)
    current_span.set_attribute("query.has_search", search is not None)
    
    if category:
        current_span.set_attribute("query.category", category)
    if search:
        current_span.set_attribute("query.search_term_length", len(search))
        # Don't store actual search term (might be PII)
    
    # ===== CACHE CHECK =====
    with tracer.start_as_current_span("cache.check") as cache_span:
        cache_key = f"books:list:{skip}:{limit}:{category}:{search}"
        cached_result = check_cache(cache_key)
        
        cache_span.set_attribute("cache.key_hash", hash(cache_key) % 10000)
        cache_span.set_attribute("cache.hit", cached_result is not None)
        cache_span.set_attribute("cache.provider", "redis")
        
        if cached_result:
            cache_span.add_event("Cache hit")
            current_span.set_attribute("result.count", len(cached_result))
            current_span.set_attribute("result.source", "cache")
            return cached_result
    
    # ===== DATABASE QUERY =====
    start_time = time.time()
    books = crud.get_books(db, skip=skip, limit=limit, category=category, search=search)
    query_duration = (time.time() - start_time) * 1000
    
    # ===== RESULT METRICS =====
    current_span.set_attribute("result.count", len(books))
    current_span.set_attribute("result.source", "database")
    current_span.set_attribute("db.query.duration_ms", query_duration)
    
    # Result size bucket
    result_bucket = "small" if len(books) < 10 else "medium" if len(books) < 50 else "large"
    current_span.set_attribute("result.size_bucket", result_bucket)
    
    # ===== CACHE UPDATE =====
    if len(books) > 0:
        with tracer.start_as_current_span("cache.set") as cache_set_span:
            cache_books(cache_key, books, ttl=300)
            cache_set_span.set_attribute("cache.ttl_seconds", 300)
            cache_set_span.add_event("Cache updated")
    
    return books
```

---

## Summary: What to Tag in Production

### Always Tag (Critical)
- `user.id` - User identification
- `user.tier` / `user.role` - User segmentation
- `tenant.id` - Multi-tenancy
- `deployment.environment` - Env (prod/staging/dev)
- `service.version` - Deployment version

### Frequently Tag (High Value)
- `error.type`, `error.message` - Error tracking
- `cache.hit` - Cache effectiveness
- `db.query.duration_ms` - DB performance
- `result.count` - Query results
- `transaction.amount` - Business metrics

### Conditionally Tag (Situational)
- `experiment.variant` - A/B testing
- `feature.flag.*` - Feature flags
- `rate_limit.exceeded` - Quota tracking
- `performance.slow` - Slow operations
- `security.*` - Audit trail

### Resource Tags (Set Once)
- `cloud.provider`, `cloud.region`
- `k8s.pod.name`, `k8s.namespace.name`
- `instance.id`, `instance.zone`
- `service.name`, `service.version`

This comprehensive tagging strategy gives you full observability into your production systems! 🎯

