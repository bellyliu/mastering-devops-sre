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
