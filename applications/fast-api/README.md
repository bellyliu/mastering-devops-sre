# FastAPI Learning Projects

Comprehensive FastAPI applications demonstrating backend development with different databases and message brokers.

## Projects Overview

### 1. PostgreSQL Book Store API
**Path:** `postgresql/`

A complete Book Store backend with:
- JWT authentication
- CRUD operations for books and users
- Redis caching
- SQLAlchemy ORM with PostgreSQL
- Search and filtering capabilities

**Key Learning:**
- PostgreSQL with SQLAlchemy
- Relational database design
- Foreign key relationships
- Connection pooling
- Transaction management

**Run:** `uvicorn app.main:app --reload --port 8000`

---

### 2. MySQL Book Store API
**Path:** `mysql/`

Enhanced Book Store backend featuring:
- Advanced filtering (price range, category)
- Statistics endpoint
- User book ownership tracking
- MySQL-specific optimizations
- CASCADE delete operations

**Key Learning:**
- MySQL with PyMySQL driver
- Boolean type handling in MySQL
- Composite indexes
- Connection recycling
- Query optimization

**Run:** `uvicorn app.main:app --reload --port 8001`

---

### 3. MongoDB Book Store API
**Path:** `mongodb/`

Modern NoSQL Book Store with:
- Async/await operations
- Beanie ODM
- Aggregation pipelines
- Flexible schema design
- Advanced pagination

**Key Learning:**
- MongoDB with Motor (async driver)
- Beanie ODM
- Document-oriented database
- Aggregation framework
- ObjectId handling
- NoSQL query patterns

**Run:** `uvicorn app.main:app --reload --port 8002`

---

### 4. RabbitMQ Pub/Sub
**Path:** `rabbitmq-pubsub/`

Event-driven architecture demonstration:
- Publisher API with FastAPI
- Multiple subscriber patterns
- Topic and Fanout exchanges
- Message routing
- Async message handling

**Key Learning:**
- RabbitMQ message broker
- Publish/Subscribe pattern
- Event-driven architecture
- aio-pika async library
- Exchange types (Topic, Fanout, Direct)
- Message acknowledgment
- Queue management

**Run Publisher:** `uvicorn publisher:app --reload --port 8003`  
**Run Subscriber:** `python subscriber.py`  
**Demo Events:** `python demo_publisher.py`

---

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL server
- MySQL server
- MongoDB server
- RabbitMQ server
- Redis server

### Installation (for any project)

```bash
# Navigate to project directory
cd postgresql/  # or mysql/ or mongodb/ or rabbitmq-pubsub/

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run the application
uvicorn app.main:app --reload  # For database projects
# OR
uvicorn publisher:app --reload  # For RabbitMQ publisher
python subscriber.py            # For RabbitMQ subscriber
```

## Learning Path

### Beginner Level
1. Start with **PostgreSQL** - understand SQL basics and CRUD operations
2. Learn authentication and authorization with JWT
3. Study Pydantic validation and FastAPI routing
4. Understand dependency injection

### Intermediate Level
1. Move to **MySQL** - learn database-specific features
2. Understand connection pooling and optimization
3. Study advanced filtering and query building
4. Learn Redis caching strategies

### Advanced Level
1. Explore **MongoDB** - NoSQL and document databases
2. Master async/await patterns
3. Learn aggregation pipelines
4. Study flexible schema design

### Event-Driven Architecture
1. Study **RabbitMQ** - message brokers and queuing
2. Understand pub/sub patterns
3. Learn message routing and exchanges
4. Master async message handling

## Feature Comparison

| Feature | PostgreSQL | MySQL | MongoDB | RabbitMQ |
|---------|-----------|-------|---------|----------|
| Database Type | SQL | SQL | NoSQL | Message Broker |
| Schema | Fixed | Fixed | Flexible | N/A |
| Async Support | Via DB | Via DB | Native | Native |
| Relationships | Foreign Keys | Foreign Keys | Embedded/Referenced | N/A |
| Transactions | Full ACID | InnoDB ACID | Replica Set | N/A |
| Caching | Redis | Redis | Redis | N/A |
| Use Case | Complex queries | Web apps | Flexible data | Event processing |

## Common Features Across Projects

### Authentication
- JWT token-based authentication
- Password hashing with bcrypt
- OAuth2 password flow
- Protected endpoints

### CRUD Operations
- Create, Read, Update, Delete
- Input validation with Pydantic
- Error handling
- Response models

### Redis Integration
- Caching frequently accessed data
- Cache invalidation strategies
- Separate Redis databases per app

### API Documentation
- Auto-generated Swagger UI
- ReDoc alternative documentation
- OpenAPI schema

## Database Setup

### PostgreSQL
```bash
# Using Docker
docker run -d --name postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=bookstore \
  -p 5432:5432 \
  postgres:15

# Or native installation
createdb bookstore
```

### MySQL
```bash
# Using Docker
docker run -d --name mysql \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=bookstore \
  -e MYSQL_USER=user \
  -e MYSQL_PASSWORD=password \
  -p 3306:3306 \
  mysql:8

# Or native installation
mysql -u root -p
CREATE DATABASE bookstore;
```

### MongoDB
```bash
# Using Docker
docker run -d --name mongodb \
  -p 27017:27017 \
  mongo:latest

# Or native installation
mongod
```

### Redis
```bash
# Using Docker
docker run -d --name redis \
  -p 6379:6379 \
  redis:latest

# Or native installation
redis-server
```

### RabbitMQ
```bash
# Using Docker
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management

# Management UI: http://localhost:15672 (guest/guest)
```

## Testing APIs

### Using cURL

```bash
# Register user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"secret123"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=secret123"

# Create book (with token)
curl -X POST "http://localhost:8000/books/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code","author":"Robert Martin","isbn":"9780132350884","price":39.99,"quantity":10}'
```

### Using Swagger UI

1. Navigate to `http://localhost:PORT/docs`
2. Click "Authorize" button
3. Enter token after login
4. Test endpoints interactively

## Project Structure

Each database project follows this structure:
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── config.py        # Settings
│   ├── database.py      # DB connection
│   ├── models.py        # DB models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # CRUD operations
│   ├── auth.py          # Authentication
│   └── routers/
│       ├── auth.py      # Auth endpoints
│       └── books.py     # Book endpoints
├── requirements.txt
├── .env.example
└── README.md
```

RabbitMQ project structure:
```
rabbitmq-pubsub/
├── publisher.py         # Publisher API
├── subscriber.py        # Consumer app
├── demo_publisher.py    # Demo script
├── rabbitmq.py         # RabbitMQ manager
├── schemas.py          # Message schemas
├── config.py
├── requirements.txt
└── README.md
```

## Key Concepts Summary

### PostgreSQL
- ACID transactions
- Complex joins
- Foreign key constraints
- Powerful query language
- JSON support (JSONB)

### MySQL
- Wide adoption
- Good performance
- Replication support
- Full-text search
- Spatial data support

### MongoDB
- Flexible schema
- Horizontal scaling (sharding)
- Rich query language
- Aggregation framework
- High write throughput

### RabbitMQ
- Reliable message delivery
- Flexible routing
- Multiple protocols (AMQP)
- Management UI
- Plugin system

## Best Practices

### Security
- Use environment variables for secrets
- Hash passwords with bcrypt
- Validate all inputs
- Implement rate limiting
- Use HTTPS in production

### Performance
- Implement caching
- Use connection pooling
- Create proper indexes
- Optimize queries
- Use async where possible

### Code Quality
- Type hints everywhere
- Comprehensive error handling
- Logging
- Unit tests
- Documentation

## Troubleshooting

### Common Issues

**Database connection failed:**
- Check if database server is running
- Verify connection string in .env
- Check firewall settings

**Import errors:**
- Ensure virtual environment is activated
- Install all requirements
- Check Python version (3.8+)

**Redis connection failed:**
- Ensure Redis server is running
- Check Redis URL in .env
- Test with `redis-cli ping`

**RabbitMQ connection failed:**
- Ensure RabbitMQ is running
- Check port 5672 is accessible
- Verify credentials

## Next Steps

After mastering these projects:
1. Add WebSocket support for real-time updates
2. Implement GraphQL with Strawberry
3. Add Celery for background tasks
4. Implement microservices architecture
5. Add Docker Compose for easy setup
6. Create Kubernetes deployments
7. Add monitoring with Prometheus/Grafana
8. Implement CI/CD pipelines
9. Add comprehensive testing
10. Deploy to cloud (AWS/GCP/Azure)

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Redis Documentation](https://redis.io/documentation)

## License

These projects are for educational purposes.
