import asyncio
from rabbitmq import RabbitMQManager
from schemas import ExchangeType
from config import get_settings

settings = get_settings()


# Callback functions for different message types
async def handle_book_created(message: dict):
    """Handle book created events"""
    print(f"📚 Book Created: {message['title']} by {message['author']}")
    print(f"   Price: ${message['price']}")
    # Add your business logic here
    # For example: update search index, send notifications, etc.


async def handle_book_updated(message: dict):
    """Handle book updated events"""
    print(f"📝 Book Updated: {message['title']}")
    # Add your business logic here


async def handle_book_deleted(message: dict):
    """Handle book deleted events"""
    print(f"🗑️  Book Deleted: {message['book_id']}")
    # Add your business logic here


async def handle_order_placed(message: dict):
    """Handle new order events"""
    print(f"🛒 New Order: #{message['order_id']}")
    print(f"   User: {message['user_id']}")
    print(f"   Total: ${message['total_amount']}")
    print(f"   Books: {len(message['books'])} item(s)")
    # Add your business logic here
    # For example: process payment, update inventory, etc.


async def handle_order_confirmed(message: dict):
    """Handle order confirmation events"""
    print(f"✅ Order Confirmed: #{message['order_id']}")
    # Add your business logic here


async def handle_notification(message: dict):
    """Handle notification events (fanout)"""
    print(f"🔔 Notification: {message['event_type']}")
    print(f"   To: {message['recipient']}")
    print(f"   Subject: {message['subject']}")
    print(f"   Message: {message['message']}")
    # Add your business logic here
    # For example: send actual email/SMS/push notification


async def handle_all_books(message: dict):
    """Handle all book-related events"""
    event_type = message.get('event_type', 'unknown')
    print(f"📖 Book Event: {event_type}")
    print(f"   Data: {message}")
    # Add your business logic here


# Subscriber configurations
SUBSCRIBERS = [
    {
        "name": "Book Created Subscriber",
        "queue": "book_created_queue",
        "exchange": "books",
        "routing_key": "book.created",
        "callback": handle_book_created
    },
    {
        "name": "Book Updated Subscriber",
        "queue": "book_updated_queue",
        "exchange": "books",
        "routing_key": "book.updated",
        "callback": handle_book_updated
    },
    {
        "name": "Book Deleted Subscriber",
        "queue": "book_deleted_queue",
        "exchange": "books",
        "routing_key": "book.deleted",
        "callback": handle_book_deleted
    },
    {
        "name": "All Books Subscriber",
        "queue": "all_books_queue",
        "exchange": "books",
        "routing_key": "book.*",  # Wildcard to match all book events
        "callback": handle_all_books
    },
    {
        "name": "Order Placed Subscriber",
        "queue": "order_placed_queue",
        "exchange": "orders",
        "routing_key": "order.placed",
        "callback": handle_order_placed
    },
    {
        "name": "Order Confirmed Subscriber",
        "queue": "order_confirmed_queue",
        "exchange": "orders",
        "routing_key": "order.confirmed",
        "callback": handle_order_confirmed
    },
    {
        "name": "Notification Subscriber 1",
        "queue": "notifications_queue_1",
        "exchange": "notifications",
        "routing_key": "",  # Fanout exchange ignores routing key
        "callback": handle_notification
    },
    {
        "name": "Notification Subscriber 2",
        "queue": "notifications_queue_2",
        "exchange": "notifications",
        "routing_key": "",  # Another subscriber to demonstrate fanout
        "callback": handle_notification
    },
]


async def start_subscriber(config: dict, manager: RabbitMQManager):
    """Start a single subscriber"""
    print(f"Starting {config['name']}...")
    
    # Bind queue to exchange
    await manager.bind_queue(
        queue_name=config['queue'],
        exchange_name=config['exchange'],
        routing_key=config['routing_key']
    )
    
    # Start consuming messages
    await manager.consume_messages(
        queue_name=config['queue'],
        callback=config['callback']
    )


async def main():
    """Main function to start all subscribers"""
    manager = RabbitMQManager()
    
    try:
        # Connect to RabbitMQ
        await manager.connect()
        
        # Declare exchanges
        await manager.declare_exchange("books", ExchangeType.TOPIC)
        await manager.declare_exchange("orders", ExchangeType.TOPIC)
        await manager.declare_exchange("notifications", ExchangeType.FANOUT)
        
        print("\n" + "="*60)
        print("RabbitMQ Subscriber Application")
        print("="*60)
        print(f"Active Subscribers: {len(SUBSCRIBERS)}")
        print("="*60 + "\n")
        
        # Start all subscribers
        tasks = []
        for config in SUBSCRIBERS:
            task = asyncio.create_task(start_subscriber(config, manager))
            tasks.append(task)
        
        # Wait for all tasks to complete (they run indefinitely)
        await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        print("\n\nShutting down subscribers...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
