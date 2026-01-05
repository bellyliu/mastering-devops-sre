# Book Store API - MySQL

A comprehensive Book Store backend API built with FastAPI and MySQL, featuring authentication, advanced CRUD operations, Redis caching, and price filtering.

## Features

- **Authentication & Authorization**: JWT-based authentication system
- **User Management**: Register, login, update, and delete user profiles
- **Book Management**: Full CRUD operations for books
- **Redis Caching**: Book data caching for improved performance
- **Advanced Filtering**: Search, category filter, and price range filtering
- **Statistics Endpoint**: Get database statistics
- **Database**: MySQL with SQLAlchemy ORM and PyMySQL driver
- **API Documentation**: Auto-generated Swagger UI and ReDoc

## Architecture

### Project Structure

```
mysql/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database and Redis connections
│   ├── models.py            # SQLAlchemy models
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

### Database Schema

#### Users Table
- `id`: INT PRIMARY KEY AUTO_INCREMENT
- `username`: VARCHAR(50) UNIQUE NOT NULL
- `email`: VARCHAR(100) UNIQUE NOT NULL
- `hashed_password`: VARCHAR(255) NOT NULL
- `full_name`: VARCHAR(100)
- `is_active`: BOOLEAN DEFAULT TRUE
- `created_at`: DATETIME DEFAULT CURRENT_TIMESTAMP
- `updated_at`: DATETIME ON UPDATE CURRENT_TIMESTAMP

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `username`
- UNIQUE INDEX on `email`

#### Books Table
- `id`: INT PRIMARY KEY AUTO_INCREMENT
- `title`: VARCHAR(200) NOT NULL
- `author`: VARCHAR(100) NOT NULL
- `isbn`: VARCHAR(13) UNIQUE
- `description`: TEXT
- `price`: FLOAT NOT NULL
- `quantity`: INT DEFAULT 0
- `category`: VARCHAR(50)
- `published_year`: INT
- `owner_id`: INT FOREIGN KEY → users(id) CASCADE DELETE
- `created_at`: DATETIME DEFAULT CURRENT_TIMESTAMP
- `updated_at`: DATETIME ON UPDATE CURRENT_TIMESTAMP

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `title`
- INDEX on `author`
- UNIQUE INDEX on `isbn`
- INDEX on `category`
- FOREIGN KEY on `owner_id`

## Key Concepts

### 1. MySQL-Specific Features

**Connection Pooling:**
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # Test connections before using
    pool_recycle=3600,       # Recycle connections every hour
)
```

**Benefits:**
- Prevents "MySQL server has gone away" errors
- Recycles stale connections automatically
- Better connection management

**Boolean Type:**
```python
# MySQL uses TINYINT(1) for boolean
is_active = Column(Boolean, default=True)
```

**CASCADE DELETE:**
```python
# When a user is deleted, their books are automatically deleted
owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
books = relationship("Book", back_populates="owner", cascade="all, delete-orphan")
```

### 2. Advanced Filtering

**Price Range Filtering:**
```python
def get_books(
    db: Session,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    query = db.query(models.Book)
    
    if min_price is not None:
        query = query.filter(models.Book.price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.Book.price <= max_price)
    
    return query.all()
```

**Combined Filters:**
```bash
GET /books/?category=Programming&min_price=20&max_price=50&search=Python
```

### 3. Redis Caching with MySQL

**Cache Key Pattern:**
```
mysql:book:{book_id}
mysql:books:*
```

**Separate Redis Database:**
```
REDIS_URL=redis://localhost:6379/1  # Database 1 for MySQL app
```

This separation allows running multiple FastAPI apps (PostgreSQL, MySQL, MongoDB) with different Redis databases.

### 4. Query Optimization

**Eager Loading with joinedload:**
```python
db_book = db.query(Book).options(joinedload(Book.owner)).filter(Book.id == book_id).first()
```

**Count Queries:**
```python
def get_books_count(db: Session):
    return db.query(func.count(Book.id)).scalar()
```

### 5. SQLAlchemy with MySQL

**LIKE Queries (Case-Insensitive):**
```python
query = query.filter(
    or_(
        Book.title.like(f"%{search}%"),
        Book.author.like(f"%{search}%")
    )
)
```

**Aggregate Functions:**
```python
from sqlalchemy import func

total_users = db.query(func.count(User.id)).scalar()
avg_price = db.query(func.avg(Book.price)).scalar()
max_price = db.query(func.max(Book.price)).scalar()
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
| GET | `/books/count` | Get total book count | No |
| GET | `/books/my-books` | Get current user's books | Yes |
| GET | `/books/{book_id}` | Get specific book | No |
| PUT | `/books/{book_id}` | Update book (owner only) | Yes |
| DELETE | `/books/{book_id}` | Delete book (owner only) | Yes |

### System

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Root endpoint | No |
| GET | `/health` | Health check | No |
| GET | `/stats` | Database statistics | No |

### Query Parameters for GET /books/

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 100)
- `category`: Filter by category
- `search`: Search in title and author fields
- `min_price`: Minimum price (inclusive)
- `max_price`: Maximum price (inclusive)

## Configuration

Create a `.env` file based on `.env.example`:

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/bookstore
REDIS_URL=redis://localhost:6379/1
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running the Application

### Prerequisites

1. MySQL server running
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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Database Setup

```sql
-- Create database
CREATE DATABASE bookstore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (optional)
CREATE USER 'bookstore_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON bookstore.* TO 'bookstore_user'@'localhost';
FLUSH PRIVILEGES;

-- The tables will be created automatically by SQLAlchemy
```

## Advanced Concepts

### 1. MySQL Connection Management

**Pool Settings:**
```python
pool_size=5          # Number of connections to maintain
max_overflow=10      # Additional connections when pool is full
pool_pre_ping=True   # Verify connection health
pool_recycle=3600    # Recycle connections after 1 hour
```

### 2. Transaction Management

SQLAlchemy handles transactions automatically:
```python
db.add(new_book)
db.commit()          # Commits transaction
db.refresh(new_book) # Refresh with DB values
```

On error:
```python
try:
    db.add(new_book)
    db.commit()
except Exception as e:
    db.rollback()    # Rollback on error
    raise e
```

### 3. Indexes for Performance

**Single Column Index:**
```python
Column(String(200), index=True)
```

**Composite Index (manual):**
```sql
CREATE INDEX idx_category_price ON books(category, price);
```

**Query Using Index:**
```python
# Uses category index
query.filter(Book.category == "Programming")

# Uses composite index (if created)
query.filter(and_(Book.category == "Programming", Book.price < 50))
```

### 4. N+1 Query Problem Solution

**Problem:**
```python
# N+1 queries
books = db.query(Book).all()
for book in books:
    print(book.owner.username)  # Triggers N additional queries
```

**Solution:**
```python
# Single query with JOIN
books = db.query(Book).options(joinedload(Book.owner)).all()
for book in books:
    print(book.owner.username)  # No additional query
```

### 5. MySQL-Specific Data Types

```python
from sqlalchemy.dialects.mysql import LONGTEXT, MEDIUMINT, ENUM

class Book(Base):
    description = Column(LONGTEXT)  # Up to 4GB text
    status = Column(ENUM('available', 'sold', 'reserved'))
```

## Testing Examples

```bash
# Register a user
curl -X POST "http://localhost:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "secret123",
    "full_name": "Alice Smith"
  }'

# Login
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret123"

# Create a book (replace TOKEN)
curl -X POST "http://localhost:8001/books/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Crash Course",
    "author": "Eric Matthes",
    "isbn": "9781593279288",
    "description": "A Hands-On, Project-Based Introduction to Programming",
    "price": 29.99,
    "quantity": 15,
    "category": "Programming",
    "published_year": 2019
  }'

# Get books with price filter
curl "http://localhost:8001/books/?min_price=20&max_price=40&category=Programming"

# Get statistics
curl "http://localhost:8001/stats"

# Get count
curl "http://localhost:8001/books/count?category=Programming"

# Get my books
curl "http://localhost:8001/books/my-books" \
  -H "Authorization: Bearer TOKEN"
```

## Performance Optimization

### 1. Connection Pooling
- Reuses database connections
- Reduces connection overhead
- Configurable pool size

### 2. Redis Caching
- Caches frequently accessed books
- TTL of 1 hour
- Cache invalidation on updates

### 3. Query Optimization
- Indexed columns for faster lookups
- Eager loading to prevent N+1 queries
- Limit and offset for pagination

### 4. Database Design
- Proper foreign keys with cascade
- Normalized schema
- Appropriate data types

## MySQL vs PostgreSQL Differences

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Boolean Type | BOOLEAN | TINYINT(1) |
| Auto Increment | SERIAL | AUTO_INCREMENT |
| Case Sensitivity | Case-sensitive by default | Case-insensitive (depends on collation) |
| JSON Support | Native JSONB | JSON (since 5.7) |
| Full-Text Search | Built-in | Built-in (different syntax) |
| Transactions | Full ACID | InnoDB is ACID |

## Common Issues & Solutions

### Issue: MySQL server has gone away
**Solution:** Use `pool_pre_ping=True` and `pool_recycle=3600`

### Issue: Character encoding problems
**Solution:** Use UTF8MB4 collation
```sql
CREATE DATABASE bookstore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Issue: Slow queries
**Solutions:**
- Add indexes on frequently queried columns
- Use EXPLAIN to analyze query performance
- Enable query cache (MySQL < 8.0)

### Issue: Deadlocks
**Solutions:**
- Keep transactions short
- Access tables in consistent order
- Use appropriate isolation levels

## Next Steps

To enhance this application:
1. Add full-text search using MySQL FULLTEXT index
2. Implement soft deletes (mark as deleted instead of removing)
3. Add book images with file upload
4. Create analytics endpoints (top books, sales trends)
5. Implement shopping cart functionality
6. Add order management
7. Create backup and restore procedures
8. Add database replication setup
9. Implement read replicas for scaling
10. Add comprehensive testing suite

## Documentation

- FastAPI Docs: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI JSON: http://localhost:8001/openapi.json

## Learning Resources

### MySQL Concepts Covered
1. Connection pooling and management
2. Foreign keys with CASCADE operations
3. Indexes for performance
4. Transaction management
5. Character sets and collations
6. Query optimization
7. SQLAlchemy with MySQL dialect
8. Database statistics and monitoring

### FastAPI Concepts Covered
1. Advanced filtering with multiple parameters
2. Statistics endpoints
3. User-specific queries
4. Count endpoints for pagination
5. Better error handling
6. Redis integration with namespacing
