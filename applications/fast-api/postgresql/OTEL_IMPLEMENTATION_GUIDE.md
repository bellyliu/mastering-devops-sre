# OpenTelemetry Implementation Guide - FastAPI + Jaeger

This guide provides step-by-step instructions to implement OpenTelemetry distributed tracing in the FastAPI Book Store application with Jaeger as the backend.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Jaeger Setup (Docker Compose)](#jaeger-setup-docker-compose)
4. [Python Dependencies](#python-dependencies)
5. [Application Instrumentation](#application-instrumentation)
6. [Testing the Implementation](#testing-the-implementation)
7. [Viewing Traces in Jaeger UI](#viewing-traces-in-jaeger-ui)
8. [Advanced Configuration](#advanced-configuration)
9. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     User Request                             │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  FastAPI Application (Port 8000)                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  OpenTelemetry Auto-Instrumentation                    │  │
│  │  ├─ FastAPI requests/responses                         │  │
│  │  ├─ SQLAlchemy database queries                        │  │
│  │  ├─ Redis operations                                   │  │
│  │  └─ Custom business logic spans                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           │ OTLP Export (Port 4318)          │
│                           ↓                                   │
└──────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  Jaeger All-in-One (Container)                               │
│  ├─ Collector (Receives traces via OTLP)                     │
│  ├─ Storage (In-memory for demo)                             │
│  ├─ Query Service                                            │
│  └─ UI (Port 16686)                                          │
└──────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  Jaeger UI (Browser: http://localhost:16686)                 │
│  - View traces                                               │
│  - Search by service, operation, tags                        │
│  - Analyze performance                                       │
│  - Visualize service dependencies                            │
└──────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- Docker and Docker Compose installed
- Existing FastAPI application running
- Python 3.11+

---

## Jaeger Setup (Docker Compose)

### Add Jaeger Service to docker-compose.yaml

The Jaeger service has been added to `docker-compose.yaml`:

```yaml
jaeger:
  image: jaegertracing/all-in-one:1.67
  container_name: jaeger
  environment:
    - COLLECTOR_OTLP_ENABLED=true
  ports:
    - "16686:16686"  # Jaeger UI
    - "4318:4318"    # OTLP HTTP receiver
  networks:
    - bookstore-network
```

**Ports Explained:**
- **16686**: Jaeger UI web interface
- **4318**: OTLP HTTP endpoint for receiving traces

### Start Jaeger

```bash
cd /Users/dekribellyliu/bellyliu/mastering-devops-sre/applications/fast-api/postgresql
docker-compose up -d jaeger
```

### Verify Jaeger is Running

```bash
# Check container status
docker-compose ps jaeger

# Access Jaeger UI
open http://localhost:16686
```

---

## Python Dependencies

### Required Packages

Add these to `requirements.txt`:

```txt
# OpenTelemetry Core
opentelemetry-api==1.29.0
opentelemetry-sdk==1.29.0

# OpenTelemetry Instrumentation
opentelemetry-instrumentation==0.50b0
opentelemetry-instrumentation-fastapi==0.50b0
opentelemetry-instrumentation-sqlalchemy==0.50b0
opentelemetry-instrumentation-redis==0.50b0
opentelemetry-instrumentation-psycopg2==0.50b0

# OTLP Exporter
opentelemetry-exporter-otlp-proto-http==1.29.0
```

### Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using Docker rebuild
docker-compose build api
docker-compose up -d api
```

---

## Application Instrumentation

### Option 1: Automatic Instrumentation (Recommended for Quick Start)

Create a new file `app/tracing.py`:

```python
"""
OpenTelemetry automatic instrumentation configuration.
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor


def configure_opentelemetry(app, service_name: str = "bookstore-api"):
    """
    Configure OpenTelemetry with automatic instrumentation.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service for tracing
    """
    # Define service resource
    resource = Resource(attributes={
        SERVICE_NAME: service_name,
        SERVICE_VERSION: "1.0.0",
        "environment": "development",
    })
    
    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)
    
    # Configure OTLP exporter to send to Jaeger
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://jaeger:4318/v1/traces",
        timeout=30,
    )
    
    # Add span processor with batching for performance
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument SQLAlchemy (will auto-detect when used)
    SQLAlchemyInstrumentor().instrument()
    
    # Instrument Redis (will auto-detect when used)
    RedisInstrumentor().instrument()
    
    # Instrument psycopg2 (PostgreSQL driver)
    Psycopg2Instrumentor().instrument()
    
    print(f"OpenTelemetry configured for service: {service_name}")
    print(f"Sending traces to: http://jaeger:4318/v1/traces")


def get_tracer(name: str):
    """
    Get a tracer for manual instrumentation.
    
    Args:
        name: Name of the tracer (usually module name)
    
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)
```

### Update `app/main.py`

Modify your main FastAPI application:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, books
from app.database import engine, Base
from app.tracing import configure_opentelemetry  # Add this import

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Store API",
    description="A simple book store API with authentication",
    version="1.0.0"
)

# Configure OpenTelemetry - MUST be done before adding routes
configure_opentelemetry(app, service_name="bookstore-api")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(books.router, prefix="/books", tags=["books"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to Book Store API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Key Points:**
- Import `configure_opentelemetry` from `app.tracing`
- Call it **before** adding routes/middleware
- Automatic instrumentation will capture all requests, DB queries, and Redis operations

---

### Option 2: Manual Instrumentation (For Custom Business Logic)

For adding custom spans to specific business operations:

#### Example 1: Custom Span in CRUD Operations

Update `app/crud.py`:

```python
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.tracing import get_tracer  # Add this import
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Get tracer
tracer = get_tracer(__name__)


def create_book(db: Session, book: schemas.BookCreate, user_id: int):
    """Create a new book with custom tracing."""
    
    # Create a custom span for business logic
    with tracer.start_as_current_span("create_book_business_logic") as span:
        # Add custom attributes
        span.set_attribute("user.id", user_id)
        span.set_attribute("book.title", book.title)
        span.set_attribute("book.author", book.author)
        
        try:
            db_book = models.Book(
                **book.dict(),
                owner_id=user_id
            )
            db.add(db_book)
            db.flush()  # Get the ID before commit
            
            # Add the book ID to span
            span.set_attribute("book.id", db_book.id)
            
            db.commit()
            db.refresh(db_book)
            
            # Mark span as successful
            span.set_status(Status(StatusCode.OK))
            span.add_event("Book created successfully")
            
            return db_book
            
        except Exception as e:
            db.rollback()
            # Record error in span
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


def get_books(db: Session, skip: int = 0, limit: int = 100):
    """Get books with performance tracking."""
    
    with tracer.start_as_current_span("get_books_query") as span:
        span.set_attribute("query.skip", skip)
        span.set_attribute("query.limit", limit)
        
        books = db.query(models.Book).offset(skip).limit(limit).all()
        
        span.set_attribute("result.count", len(books))
        span.add_event(f"Retrieved {len(books)} books")
        
        return books


def delete_book(db: Session, book_id: int, user_id: int):
    """Delete book with authorization tracking."""
    
    with tracer.start_as_current_span("delete_book_operation") as span:
        span.set_attribute("book.id", book_id)
        span.set_attribute("user.id", user_id)
        
        # Find book
        with tracer.start_as_current_span("fetch_book_for_deletion"):
            book = db.query(models.Book).filter(models.Book.id == book_id).first()
        
        if not book:
            span.add_event("Book not found")
            span.set_status(Status(StatusCode.ERROR, "Book not found"))
            return None
        
        # Check ownership
        with tracer.start_as_current_span("verify_book_ownership"):
            if book.owner_id != user_id:
                span.add_event("Unauthorized deletion attempt")
                span.set_attribute("error.type", "unauthorized")
                span.set_status(Status(StatusCode.ERROR, "Unauthorized"))
                raise PermissionError("Not authorized to delete this book")
        
        # Delete
        with tracer.start_as_current_span("execute_delete"):
            db.delete(book)
            db.commit()
        
        span.add_event("Book deleted successfully")
        span.set_status(Status(StatusCode.OK))
        
        return True
```

#### Example 2: Custom Span in Authentication

Update `app/auth.py`:

```python
import hashlib
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import settings
from app.tracing import get_tracer  # Add this
from opentelemetry.trace import Status, StatusCode

tracer = get_tracer(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with tracing."""
    
    with tracer.start_as_current_span("verify_password") as span:
        # Don't log password values!
        span.set_attribute("operation", "password_verification")
        
        try:
            prepared_password = _prepare_password(plain_password)
            result = bcrypt.checkpw(prepared_password, hashed_password.encode('utf-8'))
            
            span.set_attribute("verification.result", "success" if result else "failed")
            span.set_status(Status(StatusCode.OK))
            
            return result
            
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT token with tracing."""
    
    with tracer.start_as_current_span("create_jwt_token") as span:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        
        # Add span attributes (avoid sensitive data)
        span.set_attribute("token.expiry", expire.isoformat())
        span.set_attribute("token.subject", data.get("sub", "unknown"))
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        span.add_event("JWT token created")
        span.set_status(Status(StatusCode.OK))
        
        return encoded_jwt
```

#### Example 3: Custom Span in Router

Update `app/routers/books.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, database
from app.dependencies import get_current_user
from app.tracing import get_tracer  # Add this
from opentelemetry import trace

router = APIRouter()
tracer = get_tracer(__name__)


@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Create a new book (with tracing)."""
    
    # Get current span (auto-created by FastAPI instrumentation)
    current_span = trace.get_current_span()
    
    # Add custom attributes to the HTTP span
    current_span.set_attribute("user.id", current_user.id)
    current_span.set_attribute("user.username", current_user.username)
    current_span.set_attribute("book.title", book.title)
    
    # Create a custom span for validation
    with tracer.start_as_current_span("validate_book_data") as span:
        if len(book.title) < 3:
            span.add_event("Validation failed: title too short")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title must be at least 3 characters"
            )
        span.add_event("Validation passed")
    
    # Database operation (auto-instrumented + custom spans from crud.py)
    db_book = crud.create_book(db=db, book=book, user_id=current_user.id)
    
    current_span.add_event("Book created successfully")
    
    return db_book


@router.get("/", response_model=List[schemas.Book])
async def read_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    """Get all books (with performance tracking)."""
    
    current_span = trace.get_current_span()
    current_span.set_attribute("pagination.skip", skip)
    current_span.set_attribute("pagination.limit", limit)
    
    books = crud.get_books(db, skip=skip, limit=limit)
    
    current_span.set_attribute("result.count", len(books))
    
    return books
```

---

## Testing the Implementation

### 1. Rebuild and Restart Services

```bash
# Rebuild API with new dependencies
docker-compose build api

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api
```

You should see:
```
OpenTelemetry configured for service: bookstore-api
Sending traces to: http://jaeger:4318/v1/traces
```

### 2. Generate Test Traffic

```bash
# Health check
curl http://localhost:8000/health

# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=Test123!"

# Create a book (replace TOKEN with the access_token from login)
curl -X POST http://localhost:8000/books/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "OpenTelemetry in Action",
    "author": "John Doe",
    "description": "Learn distributed tracing",
    "year": 2025,
    "isbn": "978-1234567890"
  }'

# Get all books
curl http://localhost:8000/books/
```

---

## Viewing Traces in Jaeger UI

### Access Jaeger UI

Open your browser: **http://localhost:16686**

### Search for Traces

1. **Select Service**: `bookstore-api`
2. **Select Operation**: 
   - `POST /auth/login`
   - `POST /books/`
   - `GET /books/`
3. **Click "Find Traces"**

### Understanding the Trace View

```
Trace Timeline View:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POST /books/ (245ms)
├─ authenticate_user (85ms)
│  └─ SELECT FROM users (PostgreSQL) (40ms)
├─ validate_book_data (5ms)
├─ create_book_business_logic (140ms)
│  ├─ INSERT INTO books (PostgreSQL) (120ms)
│  └─ Book created successfully (event)
└─ cache_invalidation (Redis) (25ms)
```

### Key Metrics to Observe

1. **Total Request Duration**: End-to-end latency
2. **Database Query Time**: How much time spent in PostgreSQL
3. **Authentication Overhead**: Time to verify JWT and fetch user
4. **Business Logic Time**: Custom span durations
5. **Error Spans**: Red-highlighted failed operations

### Service Dependency Graph

1. Click **"System Architecture"** tab
2. See visual graph:
   ```
   bookstore-api → PostgreSQL
   bookstore-api → Redis
   ```

---

## Advanced Configuration

### Custom Sampling Strategy

Update `app/tracing.py`:

```python
from opentelemetry.sdk.trace.sampling import (
    TraceIdRatioBased,
    ParentBased,
    AlwaysOn,
    AlwaysOff
)


def configure_opentelemetry(app, service_name: str = "bookstore-api"):
    # Sampling: 10% of traces in production
    sampler = ParentBased(root=TraceIdRatioBased(0.1))
    
    # For development: sample everything
    # sampler = AlwaysOn()
    
    tracer_provider = TracerProvider(
        resource=resource,
        sampler=sampler  # Add sampler
    )
    # ... rest of configuration
```

### Add Custom Resource Attributes

```python
from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
    SERVICE_VERSION,
    SERVICE_NAMESPACE,
    DEPLOYMENT_ENVIRONMENT,
)
import socket


resource = Resource(attributes={
    SERVICE_NAME: service_name,
    SERVICE_VERSION: "1.0.0",
    SERVICE_NAMESPACE: "bookstore",
    DEPLOYMENT_ENVIRONMENT: "development",
    "service.instance.id": socket.gethostname(),
    "service.region": "us-east-1",
})
```

### Environment-Based Configuration

Update `app/config.py`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Existing settings...
    
    # OpenTelemetry settings
    OTEL_ENABLED: bool = True
    OTEL_SERVICE_NAME: str = "bookstore-api"
    OTEL_EXPORTER_ENDPOINT: str = "http://jaeger:4318/v1/traces"
    OTEL_SAMPLING_RATE: float = 1.0  # 100% for dev, 0.1 for prod
    
    class Config:
        env_file = ".env"


settings = Settings()
```

Then update `tracing.py`:

```python
from app.config import settings


def configure_opentelemetry(app):
    if not settings.OTEL_ENABLED:
        print("⚠️  OpenTelemetry is disabled")
        return
    
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_EXPORTER_ENDPOINT,
        timeout=30,
    )
    
    sampler = TraceIdRatioBased(settings.OTEL_SAMPLING_RATE)
    
    # ... rest of configuration
```

### Filter Sensitive Endpoints

Skip tracing for certain endpoints:

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


# Exclude specific endpoints from tracing
excluded_urls = "/health,/metrics,/favicon.ico"

FastAPIInstrumentor.instrument_app(
    app,
    excluded_urls=excluded_urls,
)
```

### Add Correlation IDs

```python
from fastapi import Request
import uuid


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to traces."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    
    # Add to current span
    current_span = trace.get_current_span()
    current_span.set_attribute("correlation.id", correlation_id)
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response
```

---

## Troubleshooting

### Issue 1: No Traces in Jaeger

**Symptoms**: Jaeger UI shows no traces

**Solutions:**
```bash
# 1. Check if Jaeger is running
docker-compose ps jaeger

# 2. Check API logs for OTEL errors
docker-compose logs api | grep -i otel

# 3. Verify network connectivity
docker-compose exec api ping jaeger

# 4. Check Jaeger collector logs
docker-compose logs jaeger | grep -i collector

# 5. Test OTLP endpoint
docker-compose exec api curl -v http://jaeger:4318/v1/traces
```

### Issue 2: Import Errors

**Symptoms**: `ModuleNotFoundError: No module named 'opentelemetry'`

**Solution:**
```bash
# Rebuild container with new dependencies
docker-compose build --no-cache api
docker-compose up -d api
```

### Issue 3: Slow Application Performance

**Symptoms**: Application is slower after adding tracing

**Solutions:**
1. **Increase batch size** in `tracing.py`:
   ```python
   span_processor = BatchSpanProcessor(
       otlp_exporter,
       max_queue_size=2048,
       max_export_batch_size=512,
   )
   ```

2. **Reduce sampling rate**:
   ```python
   sampler = TraceIdRatioBased(0.1)  # Sample only 10%
   ```

3. **Use asynchronous export** (already default with BatchSpanProcessor)

### Issue 4: Missing Database Spans

**Symptoms**: SQL queries not showing in traces

**Solution:**
```python
# Ensure SQLAlchemy instrumentation is called BEFORE creating engine
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

SQLAlchemyInstrumentor().instrument()

# Then create your engine
from app.database import engine
```

### Issue 5: Container Communication Issues

**Symptoms**: `Connection refused` errors

**Solution:**
```yaml
# Ensure all services are on the same network in docker-compose.yaml
services:
  api:
    networks:
      - bookstore-network
  
  jaeger:
    networks:
      - bookstore-network

networks:
  bookstore-network:
    driver: bridge
```

---

## Performance Impact

### Expected Overhead

- **Automatic instrumentation**: ~2-5% latency increase
- **Manual spans**: ~0.1-0.5ms per span
- **Memory**: ~10-20MB additional RAM

### Optimization Tips

1. **Use sampling in production**
   - Development: 100%
   - Staging: 50%
   - Production: 5-10%

2. **Batch exports**
   - Default BatchSpanProcessor is optimized
   - Exports every 5 seconds or 512 spans

3. **Avoid over-instrumentation**
   - Don't create spans for simple operations (< 1ms)
   - Focus on I/O operations and business logic

4. **Use asynchronous exporters**
   - BatchSpanProcessor exports in background
   - Doesn't block request handling

---

## Production Checklist

- [ ] Set sampling rate to 5-10%
- [ ] Use environment variables for configuration
- [ ] Enable trace ID in logs for correlation
- [ ] Set up alerts for trace export failures
- [ ] Monitor OTLP exporter performance
- [ ] Exclude health check endpoints from tracing
- [ ] Add resource attributes (region, version, etc.)
- [ ] Test failover if Jaeger is unavailable
- [ ] Document custom span naming conventions
- [ ] Set up persistent storage for Jaeger (Cassandra/Elasticsearch)

---

## Next Steps

1. **Explore Jaeger UI**: Familiarize yourself with trace search and visualization
2. **Add Custom Spans**: Instrument critical business logic
3. **Set Up Alerts**: Monitor for performance regressions
4. **Integrate Metrics**: Add OpenTelemetry metrics alongside traces
5. **Production Setup**: Use external Jaeger with persistent storage

---

## References

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [FastAPI Instrumentation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html)
- [OTLP Specification](https://opentelemetry.io/docs/specs/otlp/)
- [Sampling Documentation](https://opentelemetry.io/docs/concepts/sampling/)
