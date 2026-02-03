# OpenTelemetry Python API Methods - Production Reference

A comprehensive guide to OpenTelemetry Python library methods commonly used in production environments.

---

## Table of Contents

1. [Tracer Methods](#tracer-methods)
2. [Span Methods](#span-methods)
3. [Context Propagation](#context-propagation)
4. [Status & Error Handling](#status--error-handling)
5. [Events & Annotations](#events--annotations)
6. [Span Links](#span-links)
7. [Sampling & Recording](#sampling--recording)
8. [Common Patterns](#common-patterns)
9. [Production Examples](#production-examples)

---

## Tracer Methods

### Getting a Tracer

```python
from opentelemetry import trace

# Get tracer for your module
tracer = trace.get_tracer(
    instrumenting_module_name=__name__,
    instrumenting_library_version="1.0.0",
    schema_url=None  # Optional schema URL
)
```

**Best Practice**: Get one tracer per module/file.

```python
# app/services/payment.py
tracer = trace.get_tracer(__name__)  # Returns "app.services.payment"

# app/services/inventory.py
tracer = trace.get_tracer(__name__)  # Returns "app.services.inventory"
```

---

### Creating Spans

#### 1. `tracer.start_span()` - Manual Span Management

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

# Manual span lifecycle
span = tracer.start_span("operation_name")
try:
    # Do work
    result = perform_operation()
    span.set_attribute("result", result)
finally:
    span.end()  # Must explicitly end the span
```

**Use Case**: When you need fine-grained control over span lifecycle.

---

#### 2. `tracer.start_as_current_span()` - Context Manager (Recommended)

```python
# Automatic span management with context manager
with tracer.start_as_current_span("operation_name") as span:
    # Span automatically started
    result = perform_operation()
    span.set_attribute("result", result)
    # Span automatically ended when exiting context
```

**Use Case**: Most common pattern - automatic cleanup, safer.

**Parameters**:
```python
with tracer.start_as_current_span(
    name="my_operation",              # Span name
    kind=trace.SpanKind.INTERNAL,     # Span kind
    attributes={"key": "value"},      # Initial attributes
    links=[],                         # Span links
    start_time=None,                  # Custom start time (nanoseconds)
    record_exception=True,            # Auto-record exceptions
    set_status_on_exception=True,     # Auto-set ERROR status on exception
    end_on_exit=True                  # Auto-end span on context exit
) as span:
    # Your code here
    pass
```

---

#### 3. `tracer.start_as_current_span()` - Decorator

```python
# Decorate functions to automatically trace them
@tracer.start_as_current_span("process_payment")
def process_payment(amount, user_id):
    # Span automatically created and managed
    current_span = trace.get_current_span()
    current_span.set_attribute("amount", amount)
    current_span.set_attribute("user_id", user_id)
    return charge_card(amount)
```

**Use Case**: Clean, reusable function tracing.

---

### Span Kinds

```python
from opentelemetry.trace import SpanKind

# 1. INTERNAL (default) - Internal operation within your service
with tracer.start_as_current_span("calculate_tax", kind=SpanKind.INTERNAL) as span:
    tax = price * 0.08

# 2. SERVER - Handling incoming request (auto-set by FastAPI instrumentation)
with tracer.start_as_current_span("handle_request", kind=SpanKind.SERVER) as span:
    response = process_request()

# 3. CLIENT - Outgoing request to external service
with tracer.start_as_current_span("call_payment_api", kind=SpanKind.CLIENT) as span:
    response = requests.post("https://api.stripe.com/charge")

# 4. PRODUCER - Producing a message (Kafka, RabbitMQ, etc.)
with tracer.start_as_current_span("publish_event", kind=SpanKind.PRODUCER) as span:
    kafka_producer.send("order_created", order_data)

# 5. CONSUMER - Consuming a message
with tracer.start_as_current_span("process_message", kind=SpanKind.CONSUMER) as span:
    process_kafka_message(message)
```

---

## Span Methods

### 1. `span.set_attribute()` - Add Metadata

```python
from opentelemetry import trace

current_span = trace.get_current_span()

# String
current_span.set_attribute("user.name", "alice")

# Integer
current_span.set_attribute("user.id", 12345)

# Float
current_span.set_attribute("transaction.amount", 99.99)

# Boolean
current_span.set_attribute("cache.hit", True)

# List (array)
current_span.set_attribute("regions", ["us-east-1", "eu-west-1"])

# Multiple attributes at once
current_span.set_attributes({
    "user.id": 12345,
    "user.tier": "premium",
    "user.region": "us-east-1"
})
```

**Production Use**: Add business context, performance metrics, debugging info.

---

### 2. `span.add_event()` - Log Important Events

```python
# Simple event
span.add_event("cache_invalidated")

# Event with timestamp
import time
span.add_event(
    "payment_processed",
    timestamp=time.time_ns()  # Nanoseconds since epoch
)

# Event with attributes
span.add_event(
    "order_validated",
    attributes={
        "order.id": "ORD-12345",
        "validation.result": "passed",
        "items.count": 5
    }
)

# Multiple events to track flow
with tracer.start_as_current_span("checkout_process") as span:
    span.add_event("cart_validated")
    validate_cart(cart)
    
    span.add_event("inventory_checked", {"available": True})
    check_inventory()
    
    span.add_event("payment_initiated", {"amount": 99.99})
    process_payment()
    
    span.add_event("order_created", {"order_id": "ORD-123"})
```

**Production Use**: Timeline of operations, debugging async flows, audit trail.

**Events vs Attributes**:
- **Attributes**: Static metadata about the whole span
- **Events**: Timestamped occurrences during span execution

---

### 3. `span.set_status()` - Mark Success or Failure

```python
from opentelemetry.trace import Status, StatusCode

# Success (explicit)
span.set_status(Status(StatusCode.OK))

# Success with description
span.set_status(Status(StatusCode.OK, "Payment processed successfully"))

# Error with message
span.set_status(Status(StatusCode.ERROR, "Payment declined"))

# Unset (default, no explicit success/error)
span.set_status(Status(StatusCode.UNSET))
```

**Status Codes**:
- `StatusCode.UNSET` - Default, operation completed (neither success nor error)
- `StatusCode.OK` - Explicit success
- `StatusCode.ERROR` - Operation failed

**Production Pattern**:
```python
with tracer.start_as_current_span("process_order") as span:
    try:
        order = create_order(cart)
        span.set_attribute("order.id", order.id)
        span.set_status(Status(StatusCode.OK))
        return order
    except PaymentDeclinedError as e:
        span.set_attribute("error.type", "payment_declined")
        span.set_status(Status(StatusCode.ERROR, "Payment declined"))
        raise
    except Exception as e:
        span.set_status(Status(StatusCode.ERROR, str(e)))
        raise
```

---

### 4. `span.record_exception()` - Track Exceptions

```python
# Basic exception recording
try:
    risky_operation()
except Exception as e:
    span.record_exception(e)
    raise

# With attributes
try:
    process_payment(amount)
except PaymentError as e:
    span.record_exception(
        exception=e,
        attributes={
            "error.recoverable": True,
            "retry.count": retry_count
        }
    )
    raise

# With timestamp
import time
try:
    operation()
except Exception as e:
    span.record_exception(
        exception=e,
        timestamp=time.time_ns()
    )
    raise
```

**What Gets Recorded**:
```python
# Exception creates an event with:
{
    "event.name": "exception",
    "exception.type": "ValueError",
    "exception.message": "Invalid input",
    "exception.stacktrace": "Traceback (most recent call last)...",
    "exception.escaped": False  # True if exception propagates out of span
}
```

**Auto-Record Pattern**:
```python
# Automatic exception recording
with tracer.start_as_current_span(
    "operation",
    record_exception=True,           # Auto-record exceptions
    set_status_on_exception=True     # Auto-set ERROR status
) as span:
    risky_operation()  # Any exception automatically recorded
```

---

### 5. `span.update_name()` - Change Span Name

```python
# Initial name
with tracer.start_as_current_span("db_operation") as span:
    query_type = determine_query_type()
    
    # Update based on runtime info
    if query_type == "SELECT":
        span.update_name("db_query_select")
    elif query_type == "INSERT":
        span.update_name("db_query_insert")
    
    execute_query()
```

**Production Use**: Dynamic span names based on actual operation performed.

---

### 6. `span.is_recording()` - Check if Span is Active

```python
current_span = trace.get_current_span()

# Only add expensive attributes if span is being recorded
if current_span.is_recording():
    # This span is being sampled and recorded
    span.set_attribute("expensive.computation", compute_stats())
    span.set_attribute("full.stack.trace", get_stack_trace())
else:
    # Span is not being recorded (sampled out)
    # Skip expensive operations
    pass
```

**Production Use**: Avoid expensive attribute computation when span is sampled out.

---

### 7. `span.get_span_context()` - Get Span Context

```python
from opentelemetry.trace import SpanContext

current_span = trace.get_current_span()
span_context = current_span.get_span_context()

# Access context information
trace_id = span_context.trace_id           # Trace ID (int)
span_id = span_context.span_id             # Span ID (int)
trace_flags = span_context.trace_flags     # Flags
trace_state = span_context.trace_state     # Trace state

# Convert to hex strings
trace_id_hex = format(trace_id, '032x')    # 32-char hex
span_id_hex = format(span_id, '016x')      # 16-char hex

# Check if valid
is_valid = span_context.is_valid           # True if valid context

# Check if sampled
is_sampled = span_context.trace_flags.sampled  # True if sampled
```

**Production Use**: Pass trace context to external systems, logging correlation.

---

### 8. `span.end()` - Manually End Span

```python
# Manual span ending (when not using context manager)
span = tracer.start_span("operation")
try:
    do_work()
finally:
    span.end()  # Always end span

# With custom end time
import time
span = tracer.start_span("operation")
do_work()
span.end(end_time=time.time_ns())  # Nanoseconds since epoch
```

**Production Use**: Rarely needed - use context manager instead.

---

## Context Propagation

### 1. `trace.get_current_span()` - Get Active Span

```python
from opentelemetry import trace

# Get the currently active span
current_span = trace.get_current_span()

# Add attributes to current span (works in nested functions)
def helper_function():
    span = trace.get_current_span()
    span.set_attribute("helper.called", True)

with tracer.start_as_current_span("parent_operation") as parent:
    helper_function()  # Can access parent span
```

---

### 2. `trace.use_span()` - Activate a Span

```python
from opentelemetry import trace

# Create span without activating
span = tracer.start_span("operation")

# Manually activate span
with trace.use_span(span, end_on_exit=True):
    # span is now the current span
    current = trace.get_current_span()
    assert current == span
    
    do_work()
# Span ends when exiting context
```

---

### 3. Context Propagation Across Services

```python
from opentelemetry import trace
from opentelemetry.propagate import inject, extract
import requests

# ===== SERVICE A: Inject context into HTTP headers =====
def call_service_b():
    headers = {}
    
    # Inject current trace context into headers
    inject(headers)
    # Headers now contain: traceparent, tracestate
    
    response = requests.post(
        "http://service-b/api/endpoint",
        headers=headers,
        json=data
    )
    return response

# ===== SERVICE B: Extract context from headers =====
from fastapi import Request

@app.post("/api/endpoint")
def endpoint(request: Request):
    # Extract trace context from incoming headers
    context = extract(request.headers)
    
    # Create span as child of extracted context
    with tracer.start_as_current_span("process_request", context=context):
        # This span is now part of the same trace
        process_data()
```

**W3C Traceparent Header Format**:
```
traceparent: 00-{trace-id}-{parent-span-id}-{flags}
Example: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
         └┬┘ └──────────────┬─────────────────┘ └──────┬───────┘ └┬┘
        version    trace-id (32 hex)        parent-id (16 hex)  flags
```

---

### 4. Baggage - Cross-Cutting Concerns

```python
from opentelemetry import baggage
from opentelemetry.context import get_current

# Set baggage (propagates across service boundaries)
ctx = baggage.set_baggage("user.id", "12345")
ctx = baggage.set_baggage("tenant.id", "acme-corp", context=ctx)

# Get baggage
user_id = baggage.get_baggage("user.id")
tenant_id = baggage.get_baggage("tenant.id")

# Clear baggage
ctx = baggage.clear()
```

**Production Use**: Propagate user/tenant context across services without adding to span attributes.

---

## Status & Error Handling

### Complete Error Handling Pattern

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

def process_order(order_id: str):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        
        try:
            # Attempt processing
            order = fetch_order(order_id)
            span.set_attribute("order.amount", order.amount)
            span.add_event("order_fetched")
            
            payment = process_payment(order)
            span.set_attribute("payment.id", payment.id)
            span.add_event("payment_processed")
            
            # Success
            span.set_status(Status(StatusCode.OK, "Order processed"))
            span.add_event("order_completed")
            return payment
            
        except PaymentDeclinedError as e:
            # Business error (expected)
            span.set_attribute("error.type", "payment_declined")
            span.set_attribute("error.reason", e.reason)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, f"Payment declined: {e.reason}"))
            span.add_event("payment_declined", {"reason": e.reason})
            raise
            
        except NetworkError as e:
            # Infrastructure error (retryable)
            span.set_attribute("error.type", "network_error")
            span.set_attribute("error.retryable", True)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, "Network error"))
            span.add_event("network_error_occurred")
            raise
            
        except Exception as e:
            # Unexpected error
            span.set_attribute("error.type", "unexpected")
            span.set_attribute("error.class", type(e).__name__)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, f"Unexpected error: {str(e)}"))
            raise
```

---

## Events & Annotations

### Rich Event Examples

```python
with tracer.start_as_current_span("batch_processing") as span:
    span.set_attribute("batch.size", len(items))
    
    # Progress tracking
    for i, item in enumerate(items):
        if i % 100 == 0:
            span.add_event(
                "batch_progress",
                attributes={
                    "processed": i,
                    "total": len(items),
                    "percentage": (i / len(items)) * 100
                }
            )
        
        process_item(item)
    
    # Final summary
    span.add_event(
        "batch_completed",
        attributes={
            "total_processed": len(items),
            "duration_seconds": time.time() - start_time
        }
    )
```

### Milestone Events

```python
with tracer.start_as_current_span("user_registration") as span:
    span.add_event("validation_started")
    validate_user_input(data)
    span.add_event("validation_completed")
    
    span.add_event("password_hashing_started")
    hashed_password = hash_password(password)
    span.add_event("password_hashing_completed")
    
    span.add_event("database_insert_started")
    user = create_user(data, hashed_password)
    span.add_event("database_insert_completed", {"user.id": user.id})
    
    span.add_event("welcome_email_queued")
    queue_welcome_email(user.email)
```

---

## Span Links

### Linking Related Traces

```python
from opentelemetry.trace import Link, SpanContext

# Scenario: Batch processing - link each item to the batch
def process_batch(items):
    with tracer.start_as_current_span("process_batch") as batch_span:
        batch_context = batch_span.get_span_context()
        
        for item in items:
            # Create individual spans linked to batch
            link = Link(
                context=batch_context,
                attributes={"link.type": "batch_parent"}
            )
            
            with tracer.start_as_current_span(
                f"process_item_{item.id}",
                links=[link]
            ) as item_span:
                process_item(item)

# Scenario: Async operations - link related spans
def handle_order(order_id):
    with tracer.start_as_current_span("handle_order") as order_span:
        order_context = order_span.get_span_context()
        
        # Create link for async payment processing
        link = Link(
            context=order_context,
            attributes={"link.type": "async_parent", "order.id": order_id}
        )
        
        # Queue async payment (separate trace, but linked)
        queue_payment_processing(order_id, links=[link])
```

**Use Cases**:
- Batch processing (link items to batch)
- Async workflows (link related async operations)
- Fan-out operations (link parallel tasks to parent)
- Causality tracking (link cause and effect)

---

## Sampling & Recording

### Check if Span is Being Recorded

```python
current_span = trace.get_current_span()

if current_span.is_recording():
    # Span is being sampled - add detailed info
    span.set_attribute("detailed.metrics", compute_expensive_metrics())
    span.set_attribute("full.request.body", request_body)
else:
    # Span is sampled out - skip expensive operations
    pass
```

### Get Sampling Decision

```python
span_context = current_span.get_span_context()

if span_context.trace_flags.sampled:
    print("This trace is being sampled and exported")
else:
    print("This trace is sampled out (not exported)")
```

---

## Common Patterns

### 1. Database Query Pattern

```python
def execute_query(query: str, params: dict):
    with tracer.start_as_current_span("database.query") as span:
        # Query info
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.operation", query.split()[0])  # SELECT, INSERT, etc.
        span.set_attribute("db.statement", query)
        
        # Performance
        start_time = time.time()
        try:
            result = db.execute(query, params)
            duration = time.time() - start_time
            
            span.set_attribute("db.rows_affected", len(result))
            span.set_attribute("db.query.duration_ms", duration * 1000)
            
            # Slow query detection
            if duration > 1.0:
                span.add_event("slow_query_detected", {
                    "duration_seconds": duration,
                    "threshold": 1.0
                })
            
            span.set_status(Status(StatusCode.OK))
            return result
            
        except Exception as e:
            span.set_attribute("db.error", str(e))
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, "Query failed"))
            raise
```

### 2. External API Call Pattern

```python
def call_external_api(url: str, method: str, data: dict):
    with tracer.start_as_current_span(
        "http.client.request",
        kind=trace.SpanKind.CLIENT
    ) as span:
        # Request metadata
        span.set_attribute("http.method", method)
        span.set_attribute("http.url", url)
        span.set_attribute("http.request.size", len(json.dumps(data)))
        
        headers = {}
        inject(headers)  # Propagate trace context
        
        start_time = time.time()
        try:
            response = requests.request(method, url, json=data, headers=headers)
            duration = time.time() - start_time
            
            # Response metadata
            span.set_attribute("http.status_code", response.status_code)
            span.set_attribute("http.response.size", len(response.content))
            span.set_attribute("http.duration_ms", duration * 1000)
            
            if response.ok:
                span.set_status(Status(StatusCode.OK))
            else:
                span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
            
            return response
            
        except requests.Timeout as e:
            span.set_attribute("http.timeout", True)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, "Request timeout"))
            raise
```

### 3. Cache Pattern

```python
def get_cached_or_compute(key: str, compute_fn):
    with tracer.start_as_current_span("cache.get_or_compute") as span:
        span.set_attribute("cache.key_hash", hash(key) % 10000)
        
        # Try cache
        with tracer.start_as_current_span("cache.get") as cache_span:
            cached = redis_client.get(key)
            cache_span.set_attribute("cache.hit", cached is not None)
            
            if cached:
                cache_span.add_event("cache_hit")
                span.set_attribute("result.source", "cache")
                return cached
        
        # Cache miss - compute
        span.add_event("cache_miss")
        
        with tracer.start_as_current_span("compute.value") as compute_span:
            value = compute_fn()
            compute_span.set_attribute("compute.result_size", len(str(value)))
        
        # Store in cache
        with tracer.start_as_current_span("cache.set") as set_span:
            redis_client.set(key, value, ex=3600)
            set_span.set_attribute("cache.ttl_seconds", 3600)
            set_span.add_event("cache_updated")
        
        span.set_attribute("result.source", "computed")
        return value
```

### 4. Retry Pattern

```python
def retry_operation(operation_fn, max_retries=3):
    with tracer.start_as_current_span("retry.operation") as span:
        span.set_attribute("retry.max_attempts", max_retries)
        
        for attempt in range(max_retries):
            span.set_attribute("retry.current_attempt", attempt + 1)
            
            try:
                with tracer.start_as_current_span(f"attempt_{attempt + 1}") as attempt_span:
                    result = operation_fn()
                    attempt_span.set_status(Status(StatusCode.OK))
                
                span.set_attribute("retry.succeeded_on_attempt", attempt + 1)
                span.add_event("retry_succeeded", {"attempt": attempt + 1})
                span.set_status(Status(StatusCode.OK))
                return result
                
            except RetryableError as e:
                span.add_event("retry_failed", {
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                
                if attempt == max_retries - 1:
                    # Last attempt failed
                    span.set_attribute("retry.exhausted", True)
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, "All retries exhausted"))
                    raise
                
                # Wait before retry
                wait_time = 2 ** attempt  # Exponential backoff
                span.add_event("retry_waiting", {"wait_seconds": wait_time})
                time.sleep(wait_time)
```

### 5. Async/Await Pattern

```python
import asyncio
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def async_operation(data):
    with tracer.start_as_current_span("async.operation") as span:
        span.set_attribute("operation.type", "async")
        
        # Async database call
        with tracer.start_as_current_span("db.async_query") as db_span:
            result = await db.fetch_one(query)
            db_span.set_attribute("db.rows", 1)
        
        # Async API call
        with tracer.start_as_current_span("http.async_request") as http_span:
            response = await http_client.get(url)
            http_span.set_attribute("http.status_code", response.status)
        
        span.set_status(Status(StatusCode.OK))
        return result

# Parallel async operations
async def parallel_operations():
    with tracer.start_as_current_span("parallel.execution") as span:
        # Create child spans for parallel tasks
        tasks = [
            async_operation(data1),
            async_operation(data2),
            async_operation(data3)
        ]
        
        results = await asyncio.gather(*tasks)
        span.set_attribute("parallel.task_count", len(tasks))
        span.add_event("all_tasks_completed")
        return results
```

---

## Production Examples

### Complete FastAPI Endpoint with All Methods

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, SpanKind
import time

router = APIRouter()
tracer = trace.get_tracer(__name__)

@router.post("/orders/", status_code=201)
async def create_order(
    request: Request,
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete production example using all OTEL methods."""
    
    # Get current span (auto-created by FastAPI instrumentation)
    root_span = trace.get_current_span()
    
    # Add attributes to root span
    root_span.set_attribute("user.id", current_user.id)
    root_span.set_attribute("user.tier", current_user.tier)
    root_span.set_attribute("order.item_count", len(order.items))
    root_span.set_attribute("order.total_amount", order.total)
    
    # Add event
    root_span.add_event("order_validation_started")
    
    operation_start = time.time()
    
    try:
        # ===== VALIDATION =====
        with tracer.start_as_current_span(
            "validate_order",
            kind=SpanKind.INTERNAL
        ) as validation_span:
            validation_span.set_attribute("validation.type", "order_data")
            
            if len(order.items) == 0:
                validation_span.add_event("validation_failed", {"reason": "empty_cart"})
                validation_span.set_status(Status(StatusCode.ERROR, "Empty cart"))
                raise HTTPException(status_code=400, detail="Cart is empty")
            
            validation_span.add_event("validation_passed")
            validation_span.set_status(Status(StatusCode.OK))
        
        # ===== INVENTORY CHECK =====
        with tracer.start_as_current_span("check_inventory") as inventory_span:
            inventory_span.set_attribute("items.count", len(order.items))
            
            for item in order.items:
                # Create child span for each item
                with tracer.start_as_current_span(f"check_item_{item.id}") as item_span:
                    item_span.set_attribute("item.id", item.id)
                    item_span.set_attribute("item.quantity_requested", item.quantity)
                    
                    available = check_inventory(item.id)
                    item_span.set_attribute("item.quantity_available", available)
                    
                    if available < item.quantity:
                        item_span.add_event("insufficient_inventory")
                        item_span.set_status(Status(StatusCode.ERROR, "Out of stock"))
                        inventory_span.set_status(Status(StatusCode.ERROR))
                        raise HTTPException(status_code=409, detail=f"Item {item.id} out of stock")
                    
                    item_span.set_status(Status(StatusCode.OK))
            
            inventory_span.add_event("all_items_available")
            inventory_span.set_status(Status(StatusCode.OK))
        
        # ===== PAYMENT PROCESSING =====
        with tracer.start_as_current_span(
            "process_payment",
            kind=SpanKind.CLIENT  # External payment gateway
        ) as payment_span:
            payment_span.set_attribute("payment.amount", order.total)
            payment_span.set_attribute("payment.currency", "USD")
            payment_span.set_attribute("payment.method", order.payment_method)
            payment_span.set_attribute("payment.gateway", "stripe")
            
            payment_start = time.time()
            
            try:
                payment_result = charge_payment(
                    amount=order.total,
                    payment_method=order.payment_method
                )
                payment_duration = time.time() - payment_start
                
                payment_span.set_attribute("payment.transaction_id", payment_result.tx_id)
                payment_span.set_attribute("payment.duration_ms", payment_duration * 1000)
                payment_span.add_event("payment_successful", {
                    "transaction_id": payment_result.tx_id
                })
                payment_span.set_status(Status(StatusCode.OK))
                
            except PaymentDeclinedError as e:
                payment_span.set_attribute("payment.declined", True)
                payment_span.set_attribute("payment.decline_reason", e.reason)
                payment_span.add_event("payment_declined", {"reason": e.reason})
                payment_span.record_exception(e)
                payment_span.set_status(Status(StatusCode.ERROR, f"Payment declined: {e.reason}"))
                raise HTTPException(status_code=402, detail="Payment declined")
        
        # ===== DATABASE OPERATIONS =====
        with tracer.start_as_current_span("create_order_record") as db_span:
            db_span.set_attribute("db.operation", "INSERT")
            db_span.set_attribute("db.table", "orders")
            
            db_start = time.time()
            
            try:
                # Create order
                db_order = Order(
                    user_id=current_user.id,
                    total=order.total,
                    payment_id=payment_result.tx_id,
                    status="pending"
                )
                db.add(db_order)
                db.flush()
                
                db_span.set_attribute("order.id", db_order.id)
                db_span.add_event("order_record_created", {"order_id": db_order.id})
                
                # Create order items
                for item in order.items:
                    order_item = OrderItem(
                        order_id=db_order.id,
                        item_id=item.id,
                        quantity=item.quantity,
                        price=item.price
                    )
                    db.add(order_item)
                
                db.commit()
                db.refresh(db_order)
                
                db_duration = time.time() - db_start
                db_span.set_attribute("db.duration_ms", db_duration * 1000)
                db_span.set_attribute("db.rows_affected", 1 + len(order.items))
                db_span.add_event("transaction_committed")
                db_span.set_status(Status(StatusCode.OK))
                
            except Exception as e:
                db.rollback()
                db_span.add_event("transaction_rolled_back")
                db_span.record_exception(e)
                db_span.set_status(Status(StatusCode.ERROR, "Database error"))
                raise
        
        # ===== CACHE INVALIDATION =====
        with tracer.start_as_current_span("invalidate_caches") as cache_span:
            cache_keys = [f"user:{current_user.id}:orders", "orders:recent"]
            cache_span.set_attribute("cache.keys_invalidated", len(cache_keys))
            
            for key in cache_keys:
                redis_client.delete(key)
                cache_span.add_event("cache_key_deleted", {"key": key})
            
            cache_span.set_status(Status(StatusCode.OK))
        
        # ===== FINAL SUCCESS =====
        total_duration = time.time() - operation_start
        
        root_span.set_attribute("order.id", db_order.id)
        root_span.set_attribute("order.status", "created")
        root_span.set_attribute("operation.total_duration_ms", total_duration * 1000)
        root_span.add_event("order_created_successfully", {
            "order_id": db_order.id,
            "total_amount": order.total,
            "duration_ms": total_duration * 1000
        })
        root_span.set_status(Status(StatusCode.OK, "Order created successfully"))
        
        return {
            "order_id": db_order.id,
            "status": "created",
            "total": order.total,
            "payment_id": payment_result.tx_id
        }
        
    except HTTPException:
        # Let FastAPI handle HTTP exceptions
        raise
        
    except Exception as e:
        # Unexpected error
        root_span.set_attribute("error.unexpected", True)
        root_span.set_attribute("error.type", type(e).__name__)
        root_span.record_exception(e)
        root_span.set_status(Status(StatusCode.ERROR, f"Unexpected error: {str(e)}"))
        root_span.add_event("unexpected_error_occurred")
        
        # Re-raise as 500
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Method Reference Quick Guide

### Tracer
| Method | Purpose | Usage |
|--------|---------|-------|
| `get_tracer(__name__)` | Get tracer instance | Once per module |
| `start_span(name)` | Create span manually | Rare, use context manager |
| `start_as_current_span(name)` | Create span with context | Primary method ⭐ |

### Span - Metadata
| Method | Purpose | Example |
|--------|---------|---------|
| `set_attribute(key, value)` | Add metadata | `span.set_attribute("user.id", 123)` |
| `set_attributes(dict)` | Add multiple attributes | `span.set_attributes({"a": 1, "b": 2})` |
| `update_name(name)` | Change span name | `span.update_name("db_query_select")` |

### Span - Status
| Method | Purpose | Example |
|--------|---------|---------|
| `set_status(Status)` | Mark success/failure | `span.set_status(Status(StatusCode.OK))` |
| `record_exception(e)` | Record exception | `span.record_exception(exception)` |

### Span - Events
| Method | Purpose | Example |
|--------|---------|---------|
| `add_event(name)` | Log timestamped event | `span.add_event("cache_hit")` |
| `add_event(name, attrs)` | Event with data | `span.add_event("order_created", {"id": 123})` |

### Span - Lifecycle
| Method | Purpose | Example |
|--------|---------|---------|
| `end()` | End span manually | `span.end()` |
| `is_recording()` | Check if span active | `if span.is_recording(): ...` |
| `get_span_context()` | Get context info | `ctx = span.get_span_context()` |

### Context
| Method | Purpose | Example |
|--------|---------|---------|
| `get_current_span()` | Get active span | `span = trace.get_current_span()` |
| `use_span(span)` | Activate span | `with trace.use_span(span): ...` |
| `inject(headers)` | Add trace to headers | `inject(http_headers)` |
| `extract(headers)` | Get trace from headers | `ctx = extract(request.headers)` |

---

## Best Practices Summary

### ✅ DO

1. **Use context manager** for automatic cleanup
   ```python
   with tracer.start_as_current_span("operation"): ...
   ```

2. **Set business attributes** for context
   ```python
   span.set_attribute("user.id", user_id)
   ```

3. **Add events** for timeline tracking
   ```python
   span.add_event("payment_processed")
   ```

4. **Record exceptions** with context
   ```python
   span.record_exception(e)
   ```

5. **Set status** explicitly for clarity
   ```python
   span.set_status(Status(StatusCode.OK))
   ```

### ❌ DON'T

1. **Forget to end spans** (use context manager!)
2. **Add sensitive data** to attributes
3. **Create too many spans** (performance overhead)
4. **Ignore is_recording()** for expensive operations
5. **Duplicate auto-instrumentation** data

---

This guide covers all major OpenTelemetry Python methods used in production! 🎯
