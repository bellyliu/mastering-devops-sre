# RabbitMQ Pub/Sub with FastAPI

A comprehensive example demonstrating publish/subscribe patterns using RabbitMQ and FastAPI with aio-pika for asynchronous message handling.

## Features

- **Asynchronous Operations**: Fully async with aio-pika
- **Multiple Exchange Types**: Topic, Fanout, Direct
- **Publisher API**: RESTful API for publishing messages
- **Subscriber Scripts**: Standalone subscribers for consuming messages
- **Event-Driven Architecture**: Book, Order, and Notification events
- **Message Routing**: Topic-based and fanout routing patterns
- **Priority Queues**: Message prioritization support
- **Durable Queues**: Persistent messages and queues
- **Multiple Subscribers**: Demonstrate fanout and topic patterns

## Architecture

### Project Structure

```
rabbitmq-pubsub/
├── publisher.py           # FastAPI publisher application
├── subscriber.py          # Subscriber application (consumers)
├── demo_publisher.py      # Demo script to publish events
├── rabbitmq.py           # RabbitMQ manager and utilities
├── schemas.py            # Pydantic schemas for events
├── config.py             # Configuration settings
├── requirements.txt
├── .env.example
└── README.md
```

### Message Flow

```
Publisher API → RabbitMQ Exchange → Queue(s) → Subscriber(s)
```

## Key Concepts

### 1. Exchange Types

**Topic Exchange:**
```python
# Routing based on patterns
# books.created → matches "books.created", "books.*", "#"
# books.updated → matches "books.updated", "books.*", "#"
await manager.declare_exchange("books", ExchangeType.TOPIC)
```

**Fanout Exchange:**
```python
# Broadcasts to all bound queues (ignores routing key)
await manager.declare_exchange("notifications", ExchangeType.FANOUT)
```

**Direct Exchange:**
```python
# Exact routing key match
await manager.declare_exchange("tasks", ExchangeType.DIRECT)
```

### 2. Routing Keys

**Exact Match:**
```
routing_key="book.created"
```

**Wildcard Patterns:**
```
routing_key="book.*"      # Matches book.created, book.updated, etc.
routing_key="*.created"   # Matches book.created, order.created, etc.
routing_key="#"           # Matches everything
```

### 3. Publisher Pattern

```python
# Publish a message
await manager.publish_message(
    exchange_name="books",
    routing_key="book.created",
    message_body={
        "event_type": "book.created",
        "book_id": "123",
        "title": "FastAPI Guide"
    },
    priority=5
)
```

### 4. Subscriber Pattern

```python
# Consume messages
async def handle_message(message: dict):
    print(f"Received: {message}")
    # Process the message

await manager.consume_messages(
    queue_name="book_created_queue",
    callback=handle_message
)
```

### 5. Queue Binding

```python
# Bind queue to exchange with routing key
await manager.bind_queue(
    queue_name="book_created_queue",
    exchange_name="books",
    routing_key="book.created"
)
```

## Event Types

### Book Events
- `book.created`: New book added
- `book.updated`: Book modified
- `book.deleted`: Book removed
- `book.price_changed`: Price updated

### Order Events
- `order.placed`: New order created
- `order.confirmed`: Payment confirmed
- `order.shipped`: Order shipped
- `order.delivered`: Order delivered
- `order.cancelled`: Order cancelled

### Notification Events
- `notification.email`: Email notification
- `notification.sms`: SMS notification
- `notification.push`: Push notification

## Configuration

Create a `.env` file based on `.env.example`:

```env
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

## Running the Application

### Prerequisites

1. RabbitMQ server running
2. Python 3.8+

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Start RabbitMQ

```bash
# Using Docker
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management

# RabbitMQ Management UI: http://localhost:15672
# Default credentials: guest/guest
```

### Run Publisher API

```bash
# Terminal 1: Start publisher API
uvicorn publisher:app --reload --host 0.0.0.0 --port 8003
```

### Run Subscriber

```bash
# Terminal 2: Start subscriber
python subscriber.py
```

### Run Demo Publisher

```bash
# Terminal 3: Publish demo events
python demo_publisher.py
```

## Usage Examples

### Using Publisher API

**Publish Book Created Event:**
```bash
curl -X POST "http://localhost:8003/publish/book" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "book.created",
    "book_id": "book123",
    "title": "Clean Code",
    "author": "Robert Martin",
    "price": 39.99
  }'
```

**Publish Order Placed Event:**
```bash
curl -X POST "http://localhost:8003/publish/order" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "order.placed",
    "order_id": "order456",
    "user_id": "user789",
    "books": [
      {"book_id": "book123", "quantity": 2, "price": 39.99}
    ],
    "total_amount": 79.98
  }'
```

**Publish Notification (Fanout):**
```bash
curl -X POST "http://localhost:8003/publish/notification" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "notification.email",
    "recipient": "user@example.com",
    "subject": "Order Confirmation",
    "message": "Your order has been confirmed!"
  }'
```

**Generic Publish:**
```bash
curl -X POST "http://localhost:8003/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "exchange": "books",
    "routing_key": "book.created",
    "message": {
      "event_type": "book.created",
      "data": {"book_id": "123", "title": "FastAPI Guide"}
    },
    "priority": 5
  }'
```

## Advanced Concepts

### 1. Message Acknowledgment

```python
# Manual acknowledgment
async with message.process():
    # Process message
    # Automatically acknowledged if no exception
    pass

# Auto acknowledgment
await manager.consume_messages(
    queue_name="my_queue",
    callback=handle_message,
    auto_ack=True  # Dangerous: message lost if processing fails
)
```

### 2. Message Priority

```python
# Publish with priority
await manager.publish_message(
    exchange_name="books",
    routing_key="book.created",
    message_body=message,
    priority=10  # Higher priority (0-10)
)
```

### 3. Message Persistence

```python
from aio_pika import DeliveryMode

# Persistent message (survives broker restart)
await manager.publish_message(
    exchange_name="books",
    routing_key="book.created",
    message_body=message,
    delivery_mode=DeliveryMode.PERSISTENT
)
```

### 4. Dead Letter Exchange

```python
# Queue with dead letter exchange
queue = await channel.declare_queue(
    "my_queue",
    arguments={
        "x-dead-letter-exchange": "dlx_exchange",
        "x-dead-letter-routing-key": "failed_messages"
    }
)
```

### 5. TTL (Time To Live)

```python
# Message TTL
message = Message(
    body=json.dumps(data).encode(),
    expiration=60000  # 60 seconds in milliseconds
)

# Queue TTL
queue = await channel.declare_queue(
    "temp_queue",
    arguments={
        "x-message-ttl": 60000  # 60 seconds
    }
)
```

### 6. QoS (Quality of Service)

```python
# Process one message at a time
await channel.set_qos(prefetch_count=1)

# Process up to 10 messages at a time
await channel.set_qos(prefetch_count=10)
```

## Pub/Sub Patterns

### 1. Topic Exchange Pattern

```
Publisher → Topic Exchange → Multiple Queues (pattern matching)

Example:
- "book.created" → book_created_queue, all_books_queue
- "book.updated" → book_updated_queue, all_books_queue
- "book.*"       → all_books_queue (wildcard)
```

### 2. Fanout Exchange Pattern

```
Publisher → Fanout Exchange → All Bound Queues

Example:
notification → notifications_queue_1
            → notifications_queue_2
            → notifications_queue_3
```

### 3. Work Queue Pattern

```
Multiple publishers → Single Queue → Multiple workers

Use case: Distribute work among multiple workers
```

### 4. RPC Pattern

```
Client → Request Queue → Server
Server → Reply Queue → Client

Use case: Request-response pattern
```

## Monitoring

### RabbitMQ Management UI

Access at: http://localhost:15672

Features:
- View exchanges, queues, and bindings
- Monitor message rates
- View connections and channels
- Manually publish/consume messages
- View queue depths

### Health Check Endpoint

```bash
curl http://localhost:8003/health
```

## Common Use Cases

### 1. Microservices Communication

```
Service A (Books) → book.created → Service B (Search Index)
                                 → Service C (Notifications)
```

### 2. Event Sourcing

```
User Action → Event → Event Store
                   → Event Processor
                   → Multiple Subscribers
```

### 3. Task Distribution

```
Web Server → Task Queue → Worker 1
                       → Worker 2
                       → Worker 3
```

### 4. Real-time Notifications

```
System Event → Fanout Exchange → WebSocket Handler
                               → Email Service
                               → SMS Service
                               → Push Notification Service
```

## Best Practices

### 1. Message Durability
- Use persistent delivery mode for important messages
- Declare durable queues and exchanges
- Implement proper error handling

### 2. Idempotency
- Design consumers to handle duplicate messages
- Use unique message IDs
- Implement deduplication logic

### 3. Error Handling
- Use dead letter exchanges for failed messages
- Implement retry logic with exponential backoff
- Log all errors properly

### 4. Performance
- Use QoS to control message flow
- Batch operations when possible
- Monitor queue depths

### 5. Security
- Use authentication (username/password)
- Enable TLS for production
- Implement authorization with vhosts

## Troubleshooting

### Issue: Connection refused
**Solution:** Ensure RabbitMQ is running
```bash
docker ps  # Check if RabbitMQ container is running
```

### Issue: Messages not being consumed
**Solution:** Check queue bindings and routing keys
```bash
# Access management UI to verify bindings
http://localhost:15672/#/queues
```

### Issue: Messages accumulating in queue
**Solution:** 
- Check if subscribers are running
- Increase number of consumers
- Optimize message processing

### Issue: Lost messages
**Solution:**
- Use persistent delivery mode
- Implement manual acknowledgment
- Set up dead letter exchanges

## Next Steps

To enhance this application:
1. Add message schemas validation
2. Implement RPC pattern for request-response
3. Add message correlation IDs
4. Implement circuit breaker pattern
5. Add distributed tracing
6. Implement message replay functionality
7. Add monitoring with Prometheus
8. Implement rate limiting
9. Add integration tests
10. Create Kubernetes deployment configs

## Documentation

- Publisher API Docs: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc
- RabbitMQ Management: http://localhost:15672

## Learning Resources

### RabbitMQ Concepts Covered
1. Exchange types (Topic, Fanout, Direct)
2. Queue declaration and binding
3. Message routing and patterns
4. Publisher/Subscriber pattern
5. Message acknowledgment
6. Message persistence and durability
7. Priority queues
8. QoS (Quality of Service)
9. Dead letter exchanges
10. Message TTL

### FastAPI with RabbitMQ
1. Async message publishing
2. Lifespan events for connection management
3. RESTful API for event publishing
4. Pydantic schemas for message validation
5. Error handling in async context

### aio-pika Features
1. Async/await support
2. Robust connections (auto-reconnect)
3. Channel and exchange management
4. Message consumption patterns
5. Priority and delivery modes

## Example Scenarios

### Scenario 1: E-commerce Order Processing

```python
# Order placed
POST /publish/order
{
  "event_type": "order.placed",
  "order_id": "12345",
  "user_id": "user789",
  "total": 99.99
}

# Consumed by:
- Inventory service (reduce stock)
- Payment service (process payment)
- Notification service (send confirmation)
```

### Scenario 2: Content Publishing

```python
# New article published
POST /publish
{
  "exchange": "content",
  "routing_key": "article.published",
  "message": {
    "article_id": "abc123",
    "title": "New Article"
  }
}

# Consumed by:
- Search indexer
- Cache invalidator
- Social media poster
- Email newsletter
```

### Scenario 3: System Monitoring

```python
# System alert
POST /publish
{
  "exchange": "alerts",
  "routing_key": "alert.critical",
  "message": {
    "level": "critical",
    "service": "database",
    "message": "High CPU usage"
  }
}

# Consumed by:
- Alert manager (PagerDuty, Slack)
- Metrics collector
- Auto-scaling service
```

## Comparison with Other Message Brokers

| Feature | RabbitMQ | Kafka | Redis Pub/Sub |
|---------|----------|-------|---------------|
| Message Persistence | Yes | Yes | No |
| Message Ordering | Per queue | Per partition | No guarantee |
| Routing | Flexible (exchanges) | Topic-based | Channel-based |
| Scalability | Vertical + Horizontal | Horizontal | Horizontal |
| Use Case | Task queues, RPC | Event streaming | Real-time, cache |
| Protocol | AMQP | Custom | RESP |
