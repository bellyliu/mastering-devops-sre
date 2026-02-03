from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, books
from .tracing import configure_opentelemetry

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Store API - PostgreSQL",
    description="A comprehensive Book Store API built with FastAPI and PostgreSQL",
    version="1.0.0"
)

# Configure OpenTelemetry - MUST be done before adding routes
configure_opentelemetry(app, service_name="bookstore-api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(books.router)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to Book Store API with PostgreSQL",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
