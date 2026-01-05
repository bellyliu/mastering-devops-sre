# Book Store API - MongoDB

A comprehensive Book Store backend API built with FastAPI and MongoDB, featuring authentication, advanced CRUD operations, aggregation pipelines, Redis caching, and async operations with Motor and Beanie ODM.

## Features

- **Async/Await**: Fully asynchronous with Motor and Beanie ODM
- **Authentication & Authorization**: JWT-based authentication system
- **User Management**: Register, login, update, and delete user profiles
- **Book Management**: Full CRUD operations for books
- **MongoDB Aggregation**: Category statistics and price analytics
- **Redis Caching**: Book data caching for improved performance
- **Advanced Filtering**: Search, category filter, price range, and sorting
- **Pagination**: Proper pagination with total count
- **Document Models**: Beanie ODM for elegant MongoDB operations
- **API Documentation**: Auto-generated Swagger UI and ReDoc

## Architecture

### Project Structure

```
mongodb/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # MongoDB and Redis connections
│   ├── models.py            # Beanie document models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # CRUD operations
│   ├── auth.py              # Authentication logic
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       └── books.py         # Book endpoints
├── requirements.txt
├── .env.example
└── README.md
```

### MongoDB Collections

#### Users Collection
```json
{
  "_id": ObjectId("..."),
  "username": "john_doe",
  "email": "john@example.com",
  "hashed_password": "$2b$12$...",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": ISODate("2024-01-05T..."),
  "updated_at": ISODate("2024-01-05T...")
}
```

**Indexes:**
- `username` (unique)
- `email` (unique)

#### Books Collection
```json
{
  "_id": ObjectId("..."),
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "9780132350884",
  "description": "A Handbook of Agile Software Craftsmanship",
  "price": 39.99,
  "quantity": 10,
  "category": "Programming",
  "published_year": 2008,
  "owner_id": "user_object_id",
  "created_at": ISODate("2024-01-05T..."),
  "updated_at": ISODate("2024-01-05T...")
}
```

**Indexes:**
- `title`
- `author`
- `isbn` (unique)
- `category`
- `owner_id`

## Key Concepts

### 1. Async/Await Pattern

**Motor - Async MongoDB Driver:**
```python
from motor.motor_asyncio import AsyncIOMotorClient

mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
```

**Beanie ODM:**
```python
from beanie import Document, Indexed

class User(Document):
    username: Indexed(str, unique=True)
    email: Indexed(EmailStr, unique=True)
    
    class Settings:
        name = "users"
```

**Benefits:**
- Non-blocking I/O operations
- Better concurrency handling
- Improved performance for I/O-bound tasks

### 2. Beanie ODM Features

**Document Definition:**
```python
class Book(Document):
    title: Indexed(str)
    author: Indexed(str)
    isbn: Indexed(str, unique=True)
    price: float
    owner_id: str
    
    class Settings:
        name = "books"
        indexes = ["title", "author", "isbn"]
```

**CRUD Operations:**
```python
# Create
book = Book(**data)
await book.insert()

# Read
book = await Book.get(book_id)
books = await Book.find(Book.category == "Programming").to_list()

# Update
book.price = 29.99
await book.save()

# Delete
await book.delete()
```

### 3. MongoDB Queries

**Regex Search (Case-Insensitive):**
```python
from beanie.operators import RegEx, Or

await Book.find(
    Or(
        RegEx(Book.title, "python", "i"),
        RegEx(Book.author, "martin", "i")
    )
).to_list()
```

**Filtering and Sorting:**
```python
books = await Book.find(
    Book.price >= 20,
    Book.price <= 50
).sort("-created_at").skip(10).limit(20).to_list()
```

**Compound Conditions:**
```python
from beanie.operators import And

book = await Book.find_one(
    And(
        Book.id == book_id,
        Book.owner_id == user_id
    )
)
```

### 4. Aggregation Pipelines

**Group By Category:**
```python
pipeline = [
    {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
result = await Book.aggregate(pipeline).to_list()
```

**Price Statistics:**
```python
pipeline = [
    {
        "$group": {
            "_id": None,
            "avg_price": {"$avg": "$price"},
            "min_price": {"$min": "$price"},
            "max_price": {"$max": "$price"},
            "total_books": {"$sum": 1}
        }
    }
]
result = await Book.aggregate(pipeline).to_list()
```

### 5. Lifespan Events

FastAPI lifespan context manager:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)
```

### 6. ObjectId Handling

**PyObjectId for Pydantic:**
```python
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
```

**Schema with ObjectId:**
```python
class BookResponse(BaseModel):
    id: str = Field(alias="_id")
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login and get token | No |
| GET | `/auth/me` | Get current user | Yes |
| PUT | `/auth/me` | Update current user | Yes |
| DELETE | `/auth/me` | Delete current user | Yes |

### Books

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/books/` | Create new book | Yes |
| GET | `/books/` | List all books (with filters) | No |
| GET | `/books/paginated` | List books with pagination | No |
| GET | `/books/count` | Get total book count | No |
| GET | `/books/stats/by-category` | Get books grouped by category | No |
| GET | `/books/stats/price` | Get price statistics | No |
| GET | `/books/my-books` | Get current user's books | Yes |
| GET | `/books/{book_id}` | Get specific book | No |
| PUT | `/books/{book_id}` | Update book (owner only) | Yes |
| DELETE | `/books/{book_id}` | Delete book (owner only) | Yes |

### Query Parameters

**GET /books/**
- `skip`: Number of records to skip
- `limit`: Maximum records to return
- `category`: Filter by category
- `search`: Search in title and author
- `min_price`: Minimum price
- `max_price`: Maximum price
- `sort_by`: Field to sort by (default: "created_at")
- `sort_order`: 1 for ascending, -1 for descending

**GET /books/paginated**
- `page`: Page number (starts from 1)
- `page_size`: Number of items per page
- `category`: Filter by category
- `search`: Search in title and author

## Configuration

Create a `.env` file based on `.env.example`:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=bookstore
REDIS_URL=redis://localhost:6379/2
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running the Application

### Prerequisites

1. MongoDB server running
2. Redis server running
3. Python 3.8+

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### MongoDB Setup

```bash
# Start MongoDB
mongod

# Or with Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Collections and indexes are created automatically by Beanie
```

## Advanced Concepts

### 1. Motor vs PyMongo

**Motor (Async):**
- Non-blocking operations
- Better for web applications
- Works with asyncio
- Required for FastAPI async endpoints

**PyMongo (Sync):**
- Blocking operations
- Simpler API
- Good for scripts and batch jobs

### 2. Beanie ODM Advantages

**Type Safety:**
- Pydantic validation
- IDE autocompletion
- Type hints

**Automatic Operations:**
- Index creation
- Schema validation
- Relationship management

**Query Builder:**
- Pythonic query syntax
- No raw MongoDB queries needed

### 3. MongoDB Indexing Strategy

**Single Field Indexes:**
```python
username: Indexed(str, unique=True)
```

**Compound Indexes (manual):**
```python
# In MongoDB shell
db.books.createIndex({ "category": 1, "price": 1 })
```

**Text Indexes:**
```python
# In MongoDB shell
db.books.createIndex({ 
    "title": "text", 
    "author": "text" 
})
```

### 4. Aggregation Use Cases

**Total Revenue by Category:**
```python
pipeline = [
    {
        "$group": {
            "_id": "$category",
            "total_revenue": {"$sum": {"$multiply": ["$price", "$quantity"]}},
            "book_count": {"$sum": 1}
        }
    },
    {"$sort": {"total_revenue": -1}}
]
```

**Books Published by Year:**
```python
pipeline = [
    {
        "$group": {
            "_id": "$published_year",
            "books": {"$push": "$title"}
        }
    },
    {"$sort": {"_id": -1}}
]
```

### 5. Transaction Support

MongoDB transactions (requires replica set):
```python
async with await mongodb_client.start_session() as session:
    async with session.start_transaction():
        await user.insert(session=session)
        await book.insert(session=session)
```

## Testing Examples

```bash
# Register a user
curl -X POST "http://localhost:8002/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bob",
    "email": "bob@example.com",
    "password": "password123",
    "full_name": "Bob Johnson"
  }'

# Login
curl -X POST "http://localhost:8002/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=bob&password=password123"

# Create a book
curl -X POST "http://localhost:8002/books/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "MongoDB: The Definitive Guide",
    "author": "Shannon Bradshaw",
    "isbn": "9781491954461",
    "description": "Powerful and Scalable Data Storage",
    "price": 49.99,
    "quantity": 8,
    "category": "Database",
    "published_year": 2019
  }'

# Get books with sorting
curl "http://localhost:8002/books/?sort_by=price&sort_order=1&category=Database"

# Get paginated books
curl "http://localhost:8002/books/paginated?page=1&page_size=10"

# Get category statistics
curl "http://localhost:8002/books/stats/by-category"

# Get price statistics
curl "http://localhost:8002/books/stats/price"
```

## Performance Optimization

### 1. Indexing
- Automatic index creation via Beanie
- Compound indexes for complex queries
- Text indexes for full-text search

### 2. Connection Pooling
- Motor handles connection pooling automatically
- Configurable pool size and timeouts

### 3. Redis Caching
- Cache frequently accessed books
- Invalidate cache on updates
- Separate Redis DB for isolation

### 4. Projection
```python
# Only fetch required fields
books = await Book.find().project(Book.title, Book.price).to_list()
```

### 5. Batch Operations
```python
# Insert multiple documents
await Book.insert_many([book1, book2, book3])

# Update multiple documents
await Book.find(Book.quantity == 0).update({"$set": {"quantity": 1}})
```

## MongoDB vs SQL Differences

| Aspect | MongoDB | SQL (PostgreSQL/MySQL) |
|--------|---------|------------------------|
| Schema | Flexible, dynamic | Fixed, predefined |
| Relationships | Embedded or referenced | Foreign keys |
| Queries | Document-based | SQL language |
| Joins | Aggregation pipelines | JOIN statements |
| Scaling | Horizontal (sharding) | Vertical (mainly) |
| Transactions | Supported (replica set) | Full ACID support |
| ObjectId | 12-byte identifier | Integer/UUID |

## Common Issues & Solutions

### Issue: Connection timeout
**Solution:** Increase timeout in connection string
```python
MONGODB_URL=mongodb://localhost:27017/?serverSelectionTimeoutMS=5000
```

### Issue: Duplicate key error
**Solution:** Ensure unique constraints are properly handled
```python
try:
    await user.insert()
except pymongo.errors.DuplicateKeyError:
    raise HTTPException(status_code=400, detail="Username exists")
```

### Issue: ObjectId not JSON serializable
**Solution:** Use Pydantic's json_encoders
```python
class Config:
    json_encoders = {ObjectId: str}
```

## Next Steps

To enhance this application:
1. Add full-text search with text indexes
2. Implement change streams for real-time updates
3. Add file upload to GridFS for book covers
4. Implement geospatial queries for store locations
5. Add time-series data for sales analytics
6. Implement data validation rules
7. Add backup and restore procedures
8. Implement sharding strategy for scaling
9. Add comprehensive logging
10. Create unit and integration tests

## Documentation

- FastAPI Docs: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc
- OpenAPI JSON: http://localhost:8002/openapi.json

## Learning Resources

### MongoDB Concepts Covered
1. Document-oriented database design
2. Beanie ODM for async operations
3. Motor async driver
4. Aggregation pipelines
5. Indexing strategies
6. Regex queries
7. Embedded vs referenced data
8. ObjectId handling

### Advanced Topics
1. Sharding for horizontal scaling
2. Replica sets for high availability
3. Change streams for real-time data
4. GridFS for file storage
5. Time-series collections
6. Geospatial indexes and queries
7. Text search capabilities
8. Schema validation rules

### FastAPI with MongoDB
1. Async endpoint implementation
2. Lifespan events for connection management
3. Beanie document models
4. Pagination strategies
5. Aggregation endpoint patterns
6. ObjectId serialization
7. Error handling with MongoDB
