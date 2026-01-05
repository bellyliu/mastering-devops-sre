# Book Store API - PostgreSQL

A comprehensive Book Store backend API built with FastAPI and PostgreSQL, featuring authentication, CRUD operations, and Redis caching.

## Features

- **Authentication & Authorization**: JWT-based authentication system
- **User Management**: Register, login, and update user profiles
- **Book Management**: Full CRUD operations for books
- **Redis Caching**: Book data caching for improved performance
- **Search & Filter**: Search books by title/author, filter by category
- **Database**: PostgreSQL with SQLAlchemy ORM
- **API Documentation**: Auto-generated Swagger UI and ReDoc

## Architecture

### Project Structure

```
postgresql/
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
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email
- `hashed_password`: Bcrypt hashed password
- `full_name`: User's full name
- `is_active`: Account status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

#### Books Table
- `id`: Primary key
- `title`: Book title
- `author`: Author name
- `isbn`: Unique ISBN (10-13 digits)
- `description`: Book description
- `price`: Book price
- `quantity`: Available quantity
- `category`: Book category
- `published_year`: Publication year
- `owner_id`: Foreign key to users table
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Key Concepts

### 1. Authentication Flow

```python
# Registration
POST /auth/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123",
  "full_name": "John Doe"
}

# Login
POST /auth/login
Form Data:
  username: john_doe
  password: securepass123

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}

# Use token in subsequent requests
Headers: Authorization: Bearer eyJhbGc...
```

### 2. Redis Caching Strategy

The application uses Redis for caching book data:

```python
# Cache key pattern
book:{book_id}

# Cache TTL: 3600 seconds (1 hour)
# Cache invalidation on UPDATE/DELETE operations
```

**Benefits:**
- Reduces database queries for frequently accessed books
- Improves response times
- Automatic cache invalidation on updates

### 3. Database Relationships

**One-to-Many**: User → Books
- A user can own multiple books
- SQLAlchemy handles the relationship automatically
- Cascade operations for data integrity

### 4. Pydantic Validation

```python
class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    isbn: str = Field(..., min_length=10, max_length=13)
    price: float = Field(..., gt=0)
    quantity: int = Field(default=0, ge=0)
    published_year: Optional[int] = Field(None, ge=1000, le=9999)
```

### 5. Dependency Injection

FastAPI's dependency injection system is used for:
- Database sessions (`get_db`)
- Redis clients (`get_redis`)
- Current user authentication (`get_current_active_user`)

```python
@router.post("/books/")
def create_book(
    book: BookCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    # Your code here
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login and get token | No |
| GET | `/auth/me` | Get current user | Yes |
| PUT | `/auth/me` | Update current user | Yes |

### Books

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/books/` | Create new book | Yes |
| GET | `/books/` | List all books (with filters) | No |
| GET | `/books/{book_id}` | Get specific book | No |
| PUT | `/books/{book_id}` | Update book (owner only) | Yes |
| DELETE | `/books/{book_id}` | Delete book (owner only) | Yes |

### Query Parameters for GET /books/

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 100)
- `category`: Filter by category
- `search`: Search in title and author fields

## Configuration

Create a `.env` file based on `.env.example`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/bookstore
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running the Application

### Prerequisites

1. PostgreSQL server running
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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Setup

```sql
-- Create database
CREATE DATABASE bookstore;

-- The tables will be created automatically by SQLAlchemy
```

## Advanced Concepts

### 1. SQLAlchemy Session Management

The application uses dependency injection for database sessions:
- Sessions are created per request
- Automatic cleanup with `finally` block
- Connection pooling for performance

### 2. Password Hashing

Uses `passlib` with bcrypt algorithm:
- Strong one-way hashing
- Salt automatically generated
- Resistant to rainbow table attacks

### 3. JWT Token Structure

```json
{
  "sub": "username",
  "exp": 1234567890
}
```

- `sub`: Subject (username)
- `exp`: Expiration timestamp
- Signed with HS256 algorithm

### 4. Error Handling

FastAPI automatically handles:
- Validation errors (422)
- Authentication errors (401)
- Not found errors (404)
- Custom HTTPExceptions

### 5. CORS Configuration

Configured to allow all origins (customize for production):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing with cURL

```bash
# Register a user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepass123"

# Create a book (replace TOKEN with actual token)
curl -X POST "http://localhost:8000/books/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "description": "A Handbook of Agile Software Craftsmanship",
    "price": 39.99,
    "quantity": 10,
    "category": "Programming",
    "published_year": 2008
  }'

# Get all books
curl "http://localhost:8000/books/"

# Search books
curl "http://localhost:8000/books/?search=clean&category=Programming"
```

## Performance Optimization

1. **Redis Caching**: Reduces database load for frequently accessed books
2. **Connection Pooling**: SQLAlchemy manages database connections efficiently
3. **Indexed Columns**: Username, email, ISBN, and title are indexed
4. **Query Optimization**: Uses SQLAlchemy's lazy loading and efficient queries
5. **Pagination**: Limits query results to prevent memory issues

## Security Best Practices

1. **Password Hashing**: Uses bcrypt for secure password storage
2. **JWT Tokens**: Stateless authentication with expiration
3. **Environment Variables**: Sensitive data in .env file
4. **Input Validation**: Pydantic schemas validate all inputs
5. **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
6. **CORS**: Configure allowed origins for production

## Learning Path

### Basic Level
1. Understand FastAPI routing and request handling
2. Learn Pydantic models for validation
3. Study SQLAlchemy ORM basics
4. Implement simple CRUD operations

### Intermediate Level
1. JWT authentication and authorization
2. Database relationships (One-to-Many)
3. Redis integration for caching
4. Query optimization and filtering
5. Dependency injection pattern

### Advanced Level
1. Custom middleware development
2. Advanced SQLAlchemy queries and joins
3. Cache invalidation strategies
4. Performance monitoring and optimization
5. Rate limiting and security hardening

## Common Issues & Solutions

### Issue: Database connection failed
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists

### Issue: Redis connection failed
- Ensure Redis server is running
- Check REDIS_URL in .env
- Test with `redis-cli ping`

### Issue: Token validation failed
- Check SECRET_KEY consistency
- Verify token hasn't expired
- Ensure correct Authorization header format

## Next Steps

To enhance this application, consider:
1. Add pagination with total count
2. Implement role-based access control (Admin/User)
3. Add book reviews and ratings
4. Implement inventory management
5. Add file upload for book covers
6. Create order management system
7. Add WebSocket for real-time updates
8. Implement rate limiting
9. Add comprehensive logging
10. Create unit and integration tests

## Documentation

- FastAPI Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
