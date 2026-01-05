from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class ExchangeType(str, Enum):
    """RabbitMQ exchange types"""
    DIRECT = "direct"
    FANOUT = "fanout"
    TOPIC = "topic"
    HEADERS = "headers"


class MessagePriority(int, Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 5
    HIGH = 10


class Message(BaseModel):
    """Generic message structure"""
    id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    event_type: str
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: MessagePriority = MessagePriority.NORMAL
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "user.created",
                "data": {"user_id": "123", "username": "john_doe"},
                "priority": 5
            }
        }


class BookEvent(BaseModel):
    """Book-related event"""
    event_type: str  # e.g., "book.created", "book.updated", "book.deleted"
    book_id: str
    title: str
    author: str
    price: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OrderEvent(BaseModel):
    """Order-related event"""
    event_type: str  # e.g., "order.placed", "order.confirmed", "order.shipped"
    order_id: str
    user_id: str
    books: list[dict]
    total_amount: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NotificationEvent(BaseModel):
    """Notification event"""
    event_type: str  # e.g., "notification.email", "notification.sms"
    recipient: str
    subject: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PublishRequest(BaseModel):
    """Request to publish a message"""
    exchange: str
    routing_key: str
    message: dict
    priority: Optional[MessagePriority] = MessagePriority.NORMAL


class PublishResponse(BaseModel):
    """Response after publishing a message"""
    success: bool
    message: str
    message_id: Optional[str] = None
