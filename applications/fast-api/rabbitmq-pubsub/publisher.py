import asyncio
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from schemas import (
    PublishRequest,
    PublishResponse,
    BookEvent,
    OrderEvent,
    NotificationEvent,
    ExchangeType
)
from rabbitmq import rabbitmq_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    await rabbitmq_manager.connect()
    
    # Declare exchanges for different event types
    await rabbitmq_manager.declare_exchange("books", ExchangeType.TOPIC)
    await rabbitmq_manager.declare_exchange("orders", ExchangeType.TOPIC)
    await rabbitmq_manager.declare_exchange("notifications", ExchangeType.FANOUT)
    
    print("Publisher application started")
    
    yield
    
    # Shutdown
    await rabbitmq_manager.disconnect()
    print("Publisher application stopped")


app = FastAPI(
    title="RabbitMQ Publisher API",
    description="FastAPI application for publishing messages to RabbitMQ",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RabbitMQ Publisher API",
        "docs": "/docs",
        "exchanges": ["books", "orders", "notifications"]
    }


@app.post("/publish", response_model=PublishResponse)
async def publish_message(request: PublishRequest):
    """
    Publish a generic message to an exchange with a routing key
    
    Example routing keys:
    - books.created
    - books.updated
    - books.deleted
    - orders.placed
    - orders.confirmed
    """
    try:
        await rabbitmq_manager.publish_message(
            exchange_name=request.exchange,
            routing_key=request.routing_key,
            message_body=request.message,
            priority=request.priority
        )
        
        return PublishResponse(
            success=True,
            message=f"Message published to exchange '{request.exchange}' with routing key '{request.routing_key}'",
            message_id=request.message.get("id")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish message: {str(e)}")


@app.post("/publish/book", response_model=PublishResponse)
async def publish_book_event(event: BookEvent):
    """
    Publish a book-related event
    
    Event types:
    - book.created: When a new book is added
    - book.updated: When a book is modified
    - book.deleted: When a book is removed
    - book.price_changed: When book price is updated
    """
    try:
        await rabbitmq_manager.publish_message(
            exchange_name="books",
            routing_key=event.event_type,
            message_body=event.model_dump()
        )
        
        return PublishResponse(
            success=True,
            message=f"Book event '{event.event_type}' published",
            message_id=event.book_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish book event: {str(e)}")


@app.post("/publish/order", response_model=PublishResponse)
async def publish_order_event(event: OrderEvent):
    """
    Publish an order-related event
    
    Event types:
    - order.placed: New order created
    - order.confirmed: Order payment confirmed
    - order.shipped: Order has been shipped
    - order.delivered: Order delivered to customer
    - order.cancelled: Order cancelled
    """
    try:
        await rabbitmq_manager.publish_message(
            exchange_name="orders",
            routing_key=event.event_type,
            message_body=event.model_dump()
        )
        
        return PublishResponse(
            success=True,
            message=f"Order event '{event.event_type}' published",
            message_id=event.order_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish order event: {str(e)}")


@app.post("/publish/notification", response_model=PublishResponse)
async def publish_notification_event(event: NotificationEvent):
    """
    Publish a notification event (fanout to all subscribers)
    
    Event types:
    - notification.email: Send email notification
    - notification.sms: Send SMS notification
    - notification.push: Send push notification
    """
    try:
        await rabbitmq_manager.publish_message(
            exchange_name="notifications",
            routing_key="",  # Fanout exchange ignores routing key
            message_body=event.model_dump()
        )
        
        return PublishResponse(
            success=True,
            message=f"Notification event '{event.event_type}' broadcasted to all subscribers"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish notification: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "rabbitmq": "connected" if rabbitmq_manager.connection else "disconnected"
    }
