import asyncio
from rabbitmq import RabbitMQManager
from schemas import ExchangeType, BookEvent, OrderEvent, NotificationEvent
from datetime import datetime


async def demo_publish_events():
    """Demo script to publish various events to RabbitMQ"""
    manager = RabbitMQManager()
    
    try:
        # Connect to RabbitMQ
        await manager.connect()
        
        # Declare exchanges
        await manager.declare_exchange("books", ExchangeType.TOPIC)
        await manager.declare_exchange("orders", ExchangeType.TOPIC)
        await manager.declare_exchange("notifications", ExchangeType.FANOUT)
        
        print("\n" + "="*60)
        print("RabbitMQ Event Publisher Demo")
        print("="*60 + "\n")
        
        # 1. Publish book created event
        print("1. Publishing book.created event...")
        book_created = BookEvent(
            event_type="book.created",
            book_id="book123",
            title="FastAPI for Beginners",
            author="John Doe",
            price=29.99
        )
        await manager.publish_message(
            exchange_name="books",
            routing_key="book.created",
            message_body=book_created.model_dump()
        )
        await asyncio.sleep(1)
        
        # 2. Publish book updated event
        print("\n2. Publishing book.updated event...")
        book_updated = BookEvent(
            event_type="book.updated",
            book_id="book123",
            title="FastAPI for Beginners - 2nd Edition",
            author="John Doe",
            price=34.99
        )
        await manager.publish_message(
            exchange_name="books",
            routing_key="book.updated",
            message_body=book_updated.model_dump()
        )
        await asyncio.sleep(1)
        
        # 3. Publish order placed event
        print("\n3. Publishing order.placed event...")
        order_placed = OrderEvent(
            event_type="order.placed",
            order_id="order456",
            user_id="user789",
            books=[
                {"book_id": "book123", "quantity": 2, "price": 34.99}
            ],
            total_amount=69.98
        )
        await manager.publish_message(
            exchange_name="orders",
            routing_key="order.placed",
            message_body=order_placed.model_dump()
        )
        await asyncio.sleep(1)
        
        # 4. Publish order confirmed event
        print("\n4. Publishing order.confirmed event...")
        order_confirmed = OrderEvent(
            event_type="order.confirmed",
            order_id="order456",
            user_id="user789",
            books=[
                {"book_id": "book123", "quantity": 2, "price": 34.99}
            ],
            total_amount=69.98
        )
        await manager.publish_message(
            exchange_name="orders",
            routing_key="order.confirmed",
            message_body=order_confirmed.model_dump()
        )
        await asyncio.sleep(1)
        
        # 5. Publish notification (fanout)
        print("\n5. Publishing notification event (fanout)...")
        notification = NotificationEvent(
            event_type="notification.email",
            recipient="user@example.com",
            subject="Order Confirmation",
            message="Your order #order456 has been confirmed!"
        )
        await manager.publish_message(
            exchange_name="notifications",
            routing_key="",  # Fanout ignores routing key
            message_body=notification.model_dump()
        )
        await asyncio.sleep(1)
        
        # 6. Publish book deleted event
        print("\n6. Publishing book.deleted event...")
        book_deleted = BookEvent(
            event_type="book.deleted",
            book_id="book999",
            title="Deleted Book",
            author="Unknown",
            price=0.0
        )
        await manager.publish_message(
            exchange_name="books",
            routing_key="book.deleted",
            message_body=book_deleted.model_dump()
        )
        
        print("\n" + "="*60)
        print("All events published successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await manager.disconnect()


if __name__ == "__main__":
    asyncio.run(demo_publish_events())
